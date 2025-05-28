import io
import os
import random
import tempfile
from io import BytesIO
from typing import BinaryIO

import pandas as pd
from aiogram.fsm.context import FSMContext
from aiogram.types import Document, Message, File
from pandas.core.interchange.dataframe_protocol import DataFrame

from bot.processors.subscription_processor import SubscriptionProcessor
from config.storage_service_config import MINIO_BUCKET_NAME
from constants.constants import AVAILABLE_FILE_FORMATS
from constants.enums import StateKeys
from constants.exceptions import NotValidFileContentType, NotValidColumnSet
from constants.phrases import InteractivePhrases, SUCCESS_PHRASES
from models import UserSubscriptionLevels
from processors.instances_db_processors import FileDBProcessor
from processors.purchase_processor import PurchaseProcessor, CheckUserActionByCurrentSub
from services.bot_services.bot_initializer import bot
from services.bot_services.buttons import ButtonOrchestrator
from services.bot_services.states import AvailableStates
from services.database import get_database_session
from services.storage_service import storage_client


class FileValidator:
    @staticmethod
    def validate_content_type(file_content_type: str):
        if file_content_type not in AVAILABLE_FILE_FORMATS:
            raise NotValidFileContentType(
                f"The file must be in formats {AVAILABLE_FILE_FORMATS}."
            )

    @classmethod
    def validate_data(cls, dataframe: DataFrame):
        width = dataframe.shape[1]

        if width < 2:
            raise NotValidColumnSet("Excel file must have at least two columns.")

        for column_index in range(1, 3):
            null_indexes = dataframe[dataframe.iloc[:, column_index].isnull()].index

            if null_indexes.empty:
                return

            raise ValueError(
                f"Column at index {column_index} contains nulls at rows: {list(null_indexes)}"
            )


class QuizProcessor(FileValidator):
    @classmethod
    async def handler_quiz_start(cls, message: Message, state: FSMContext):
        state_data = await state.get_data()
        file_bytes = state_data.get(StateKeys.UPLOADED_FILE_DATA.value)

        if file_bytes:
            await cls.process_file_with_words(
                file_data=BytesIO(file_bytes), message=message, state=state
            )
            return

        await message.answer(InteractivePhrases.EMPTY_FILE.value)
        await state.clear()
        return

    @classmethod
    async def ask_user_to_send_file(cls, message: Message) -> None:
        await message.answer(InteractivePhrases.ASK_TO_SEND_FILE.value)

    @classmethod
    async def success_file_get(cls, message: Message) -> None:
        await message.answer(InteractivePhrases.ASK_TO_SEND_FILE.value)

    @classmethod
    async def process_user_new_file(cls, message: Message, state: FSMContext):
        document: Document = message.document
        file: File = await message.bot.get_file(file_id=document.file_id)
        file_data: BinaryIO = await message.bot.download_file(file_path=file.file_path)
        file_data_in_bytes: bytes = file_data.read()

        try:
            await cls.validate_file_format(
                file_data_in_bytes=file_data_in_bytes,
                file_content_type=document.file_name.split(".")[1],
            )
        except Exception as e:
            print("FILE VALIDATION ERROR", str(e))
            await message.answer(InteractivePhrases.EMPTY_FILE.value)
            return

        await cls.start_quiz_with_valid_file_data(
            state=state, message=message, file_data_in_bytes=file_data_in_bytes
        )

        await cls.create_file_in_storage_client(
            message=message, file=file, file_data=file_data_in_bytes
        )

    @classmethod
    async def process_xlsx_file(
            cls,
            file_data_in_bytes: bytes,
            file_content_type: str,
            message: Message,
            state: FSMContext,
    ):
        try:
            await cls.validate_file_format(
                file_data_in_bytes=file_data_in_bytes,
                file_content_type=file_content_type,
            )

            await cls.start_quiz_with_valid_file_data(
                state=state, message=message, file_data_in_bytes=file_data_in_bytes
            )
        except Exception as e:
            await message.answer(str(e))

    @classmethod
    async def validate_file_format(
            cls, file_content_type: str, file_data_in_bytes: bytes
    ):
        cls.validate_content_type(file_content_type=file_content_type)

        file_buffer = BytesIO(file_data_in_bytes)
        file_data_in_dataframe = pd.read_excel(file_buffer)
        cls.validate_data(dataframe=file_data_in_dataframe)

    @staticmethod
    async def start_quiz_with_valid_file_data(
            state: FSMContext, file_data_in_bytes: bytes, message: Message
    ):
        await state.update_data(
            {StateKeys.UPLOADED_FILE_DATA.value: file_data_in_bytes}
        )

        if await QuizProcessor.stop_quiz(message=message, state=state):
            return

        await QuizProcessor.handler_quiz_start(message=message, state=state)

    @classmethod
    async def process_previous_user_file(cls, message: Message, state: FSMContext):
        file_response = None

        try:
            file_response = storage_client.get_object(
                bucket_name=MINIO_BUCKET_NAME, object_name=f"{message.chat.id}.xlsx"
            )
            file_data_in_bytes: bytes = file_response.read()

        except Exception as e:
            await message.answer(InteractivePhrases.EMPTY_FILE.value)
            print(f"\nUSER BUG. USER ID {message.chat.id}")
            print(str(e), "\n")
            return

        finally:
            if file_response:
                file_response.close()
                file_response.release_conn()

        await cls.start_quiz_with_valid_file_data(
            state=state, message=message, file_data_in_bytes=file_data_in_bytes
        )

    @staticmethod
    async def create_file_in_storage_client(
            message: Message, file: File, file_data: bytes
    ):
        file_content_type = file.file_path.split(".")[1]

        with tempfile.NamedTemporaryFile(
                delete=False, suffix=f".{file_content_type}"
        ) as tmp_file:
            tmp_file.write(file_data)
            tmp_file_path = tmp_file.name

        object_name = f"{message.chat.id}.{file_content_type}"
        buf = io.BytesIO(file_data)

        storage_client.put_object(
            bucket_name=MINIO_BUCKET_NAME,
            object_name=object_name,
            data=buf,
            length=buf.getbuffer().nbytes,
        )

        file_link_in_minio = storage_client.presigned_get_object(
            MINIO_BUCKET_NAME, object_name
        )

        task = FileDBProcessor(session=next(get_database_session()))
        task.create_file_link_if_not_exists(
            user_id=message.chat.id, file_link=file_link_in_minio
        )

        os.remove(tmp_file_path)

    @staticmethod
    async def process_file_with_words(
            file_data: BinaryIO, message: Message, state: FSMContext
    ):
        try:
            df = pd.read_excel(BytesIO(file_data.read()))
            word_pairs = dict(df.itertuples(index=False, name=None))

            state_data = await state.get_data()
            word_pairs = list(word_pairs.items())

            random.shuffle(word_pairs)

            word_pairs = dict(word_pairs)

            current_word = random.choice(list(word_pairs.keys()))

            await state.set_data(
                {
                    StateKeys.QUIZ_DATA.value: word_pairs,
                    StateKeys.CURRENT_WORD.value: current_word,
                    StateKeys.CURRENT_TRANSLATION.value: word_pairs[current_word],
                }
            )

            await state.set_state(AvailableStates.process_user_word_answer)

            await message.answer(
                InteractivePhrases.START_QUIZ.value.format(
                    len_of_pairs=len(word_pairs),
                )
            )
            await message.answer(
                text=InteractivePhrases.START_FIRST_QUIZ_WORD.value.format(
                    current_word=current_word,
                ),
                reply_markup=ButtonOrchestrator.generate_word_buttons(),
            )
        except Exception as e:
            await message.answer(f"Failed to read Excel file: {e}")
            await ButtonOrchestrator.set_menu_buttons(bot)

    @staticmethod
    def normalize_apostrophes(text: str) -> str:
        return (
            text.replace("ʼ", "'")
            .replace("’", "'")
            .replace("‘", "'")
            .replace("`", "'")
            .replace("ʹ", "'")
        )

    @classmethod
    async def process_user_answer(cls, message: Message, state: FSMContext):
        state_data = await state.get_data()
        quiz_data: dict = state_data.get(StateKeys.QUIZ_DATA.value, {})
        current_word: str = state_data.get(StateKeys.CURRENT_WORD.value)

        if not quiz_data or not current_word:
            await message.answer(InteractivePhrases.FINISH_QUIZ.value)
            await ButtonOrchestrator.set_menu_buttons(bot)
            await state.clear()
            return

        correct_answer = str(quiz_data[current_word]).strip().lower()
        user_answer = message.text.strip().lower()
        correct_answer = cls.normalize_apostrophes(correct_answer)
        user_answer = cls.normalize_apostrophes(user_answer)

        if user_answer == correct_answer:
            quiz_data.pop(current_word)

            if not quiz_data:
                await message.answer(random.choice(SUCCESS_PHRASES))
                await ButtonOrchestrator.set_menu_buttons(bot)
                await state.clear()
                return

            next_word = random.choice(list(quiz_data.keys()))
            await state.set_data(
                {
                    StateKeys.QUIZ_DATA.value: quiz_data,
                    StateKeys.CURRENT_WORD.value: next_word,
                    StateKeys.CURRENT_TRANSLATION.value: quiz_data[next_word],
                }
            )

            await message.answer(
                InteractivePhrases.CORRECT_USER_WORD.value.format(
                    next_original_word=next_word,
                ),
                reply_markup=ButtonOrchestrator.generate_word_buttons(),
            )

        else:
            await message.answer(
                InteractivePhrases.INCORRECT_USER_WORD.value.format(
                    correct_answer=correct_answer, next_word=current_word
                )
            )

    @staticmethod
    async def stop_quiz(message: Message, state: FSMContext):
        if message.text:
            if message.text.strip().lower() == "/stop_quiz":
                await state.clear()
                await message.answer(
                    text=InteractivePhrases.STOP_QUIZ.value,
                )
                return True

        return False

    @staticmethod
    async def start_quiz_with_b1_words(message: Message, state: FSMContext):
        PurchaseProcessor.check_purchase_status(
            user_id=message.chat.id, session=next(get_database_session())
        )
        need_sub_levels = [
            UserSubscriptionLevels.FREE_TERM,
            UserSubscriptionLevels.PRO,
            UserSubscriptionLevels.PROMOCODE,
        ]

        if await PurchaseProcessor.compare_user_action_with_sub_level(
                request=CheckUserActionByCurrentSub(
                    user_id=message.chat.id, required_sub_levels=need_sub_levels
                )
        ):
            file_path = "constants/files/B1 LEVEL WORDS.xlsx"
            file_content_type = os.path.splitext(file_path)[1]

            with open(file_path, "rb") as file:
                file_data_in_bytes = file.read()

            await QuizProcessor.process_xlsx_file(
                message=message,
                file_content_type=file_content_type,
                state=state,
                file_data_in_bytes=file_data_in_bytes,
            )

        else:
            await message.answer(
                InteractivePhrases.LOW_SUBSCRIPTION_LEVEL.value,
                reply_markup=ButtonOrchestrator.set_subscription_buttons(),
            )
            return

    @staticmethod
    async def start_quiz_with_a2_words(message: Message, state: FSMContext):
        PurchaseProcessor.check_purchase_status(
            user_id=message.chat.id, session=next(get_database_session())
        )
        need_sub_levels = [
            UserSubscriptionLevels.FREE_TERM,
            UserSubscriptionLevels.START,
            UserSubscriptionLevels.PRO,
            UserSubscriptionLevels.PROMOCODE,
        ]

        if await PurchaseProcessor.compare_user_action_with_sub_level(
                request=CheckUserActionByCurrentSub(
                    user_id=message.chat.id, required_sub_levels=need_sub_levels
                )
        ):
            file_path = "constants/files/A2 LEVEL WORDS.xlsx"
            file_content_type = os.path.splitext(file_path)[1]

            with open(file_path, "rb") as file:
                file_data_in_bytes = file.read()

            await QuizProcessor.process_xlsx_file(
                message=message,
                file_content_type=file_content_type,
                state=state,
                file_data_in_bytes=file_data_in_bytes,
            )

        else:
            await message.answer(
                InteractivePhrases.LOW_SUBSCRIPTION_LEVEL.value,
                reply_markup=ButtonOrchestrator.set_subscription_buttons(),
            )
            return

    @staticmethod
    async def start_quiz_with_travel_words(message: Message, state: FSMContext):
        PurchaseProcessor.check_purchase_status(
            user_id=message.chat.id, session=next(get_database_session())
        )
        need_sub_levels = [
            UserSubscriptionLevels.FREE_TERM,
            UserSubscriptionLevels.START,
            UserSubscriptionLevels.PRO,
            UserSubscriptionLevels.PROMOCODE,
        ]

        if await PurchaseProcessor.compare_user_action_with_sub_level(
                request=CheckUserActionByCurrentSub(
                    user_id=message.chat.id, required_sub_levels=need_sub_levels
                )
        ):
            file_path = "constants/files/TRAVEL WORDS.xlsx"
            file_content_type = os.path.splitext(file_path)[1]

            with open(file_path, "rb") as file:
                file_data_in_bytes = file.read()

            await QuizProcessor.process_xlsx_file(
                message=message,
                file_content_type=file_content_type,
                state=state,
                file_data_in_bytes=file_data_in_bytes,
            )

        else:
            await message.answer(
                InteractivePhrases.LOW_SUBSCRIPTION_LEVEL.value,
                reply_markup=ButtonOrchestrator.set_subscription_buttons(),
            )
            return

    @staticmethod
    async def start_quiz_with_users_previous_file(message: Message, state: FSMContext):
        PurchaseProcessor.check_purchase_status(
            user_id=message.chat.id, session=next(get_database_session())
        )

        need_sub_levels = [
            UserSubscriptionLevels.FREE_TERM,
            UserSubscriptionLevels.SIMPLE,
            UserSubscriptionLevels.START,
            UserSubscriptionLevels.PRO,
            UserSubscriptionLevels.PROMOCODE,
        ]

        if await PurchaseProcessor.compare_user_action_with_sub_level(
                request=CheckUserActionByCurrentSub(
                    user_id=message.chat.id, required_sub_levels=need_sub_levels
                )
        ):
            await message.answer(InteractivePhrases.SUCCESS_GET_PREVIOUS_FILE.value)

            file_response = None
            try:
                file_response = storage_client.get_object(
                    bucket_name=MINIO_BUCKET_NAME, object_name=f"{message.chat.id}.xlsx"
                )
                file_data_in_bytes: bytes = file_response.read()

            except Exception as e:
                await message.answer(InteractivePhrases.EMPTY_FILE.value)
                print(f"\nUSER BUG. USER ID {message.chat.id}")
                print(str(e), "\n")
                return

            finally:
                if file_response:
                    file_response.close()
                    file_response.release_conn()

            await state.update_data(
                {StateKeys.UPLOADED_FILE_DATA.value: file_data_in_bytes}
            )

            if (
                    await QuizProcessor.stop_quiz(message=message, state=state)
                    or not message.text
            ):
                return

            await QuizProcessor.handler_quiz_start(message=message, state=state)

        else:
            await message.answer(
                InteractivePhrases.LOW_SUBSCRIPTION_LEVEL.value,
                reply_markup=ButtonOrchestrator.set_subscription_buttons(),
            )
            return

    @staticmethod
    async def start_quiz_with_new_file(message: Message, state: FSMContext):
        await SubscriptionProcessor.check_purchase_status(message=message)

        need_sub_levels = [
            UserSubscriptionLevels.FREE_TERM,
            UserSubscriptionLevels.SIMPLE,
            UserSubscriptionLevels.START,
            UserSubscriptionLevels.PRO,
            UserSubscriptionLevels.PROMOCODE,
        ]

        if await PurchaseProcessor.compare_user_action_with_sub_level(
                request=CheckUserActionByCurrentSub(
                    user_id=message.chat.id, required_sub_levels=need_sub_levels
                )
        ):
            await state.set_state(AvailableStates.awaiting_file_upload)

        else:
            await message.answer(
                InteractivePhrases.LOW_SUBSCRIPTION_LEVEL.value,
                reply_markup=ButtonOrchestrator.set_subscription_buttons(),
            )
            return
