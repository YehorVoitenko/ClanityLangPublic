import io
import logging
import os
import random
import tempfile
from io import BytesIO
from typing import BinaryIO

import pandas as pd
from aiogram.fsm.context import FSMContext
from aiogram.types import Document, Message, File
from pandas.core.interchange.dataframe_protocol import DataFrame

from config.storage_service_config import MINIO_BUCKET_NAME
from constants.constants import AVAILABLE_FILE_FORMATS
from constants.enums import StateKeys
from constants.exceptions import NotValidFileContentType, NotValidColumnSet
from constants.phrases import (
    InteractivePhrases,
    SUCCESS_PHRASES,
    CORRECT_WORD_PHRASES,
    MOTIVATION_PHRASES_FOR_MISTAKES,
)
from processors.instances_db_processors import FileDBProcessor
from processors.user_activity_processor import UserActivityProcessor
from services.bot_services.bot_initializer import bot
from services.bot_services.buttons import ButtonOrchestrator
from services.bot_services.states import AvailableStates
from services.cache_service.cache_service import words_redis_client
from services.cache_service.schemas import WordsCache
from services.database import get_database_session
from services.gpt_service.client import make_check_prompt, ask_gpt_async
from services.storage_service import storage_client

logging.basicConfig(level=logging.INFO)


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

        await message.answer(
            InteractivePhrases.EMPTY_FILE.value, disable_notification=True
        )
        await state.clear()
        return

    @classmethod
    async def ask_user_to_send_file(cls, message: Message) -> None:
        await message.answer(
            text=InteractivePhrases.ASK_TO_SEND_FILE.value, disable_notification=True
        )

    @classmethod
    async def success_file_get(cls, message: Message) -> None:
        await message.answer(
            text=InteractivePhrases.ASK_TO_SEND_FILE.value, disable_notification=True
        )

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
            await message.answer(
                text=InteractivePhrases.EMPTY_FILE.value, disable_notification=True
            )
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
        UserActivityProcessor.user_added_file(message.chat.id)

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
                text=InteractivePhrases.START_QUIZ.value.format(
                    len_of_pairs=len(word_pairs),
                ),
                disable_notification=True,
            )
            await message.answer(
                text=InteractivePhrases.START_FIRST_QUIZ_WORD.value.format(
                    current_word=current_word,
                ),
                reply_markup=ButtonOrchestrator.generate_word_buttons(),
                disable_notification=True,
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
            await message.answer(
                text=InteractivePhrases.FINISH_QUIZ.value, disable_notification=True
            )
            await ButtonOrchestrator.set_menu_buttons(bot)
            await state.clear()
            return

        correct_translation = str(quiz_data[current_word]).strip().lower()
        correct_translation = cls.normalize_apostrophes(correct_translation)
        user_translation = message.text.strip().lower()
        user_translation = cls.normalize_apostrophes(user_translation)

        prompt = make_check_prompt(
            word=current_word,
            correct_translation=correct_translation,
            user_translation=user_translation,
        )
        result = await ask_gpt_async(prompt=prompt)

        if result.startswith("✅") or result.startswith("ℹ"):
            UserActivityProcessor.user_write_correct_word(
                message.chat.id,
                original_word=current_word,
                translated_word=user_translation,
            )

            quiz_data.pop(current_word)

            if not quiz_data:
                await message.answer(
                    text=random.choice(SUCCESS_PHRASES), disable_notification=True
                )
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
                text=f"{random.choice(CORRECT_WORD_PHRASES)}\n\n"
                     f"{InteractivePhrases.CORRECT_USER_WORD.value.format(next_original_word=next_word)}",
                reply_markup=ButtonOrchestrator.generate_word_buttons(),
                disable_notification=True,
            )

        else:
            UserActivityProcessor.user_write_wrong_word(
                message.chat.id,
                original_word=current_word,
                translated_word=user_translation,
            )
            await message.answer(
                text=f"{random.choice(MOTIVATION_PHRASES_FOR_MISTAKES)}\n\n"
                     f"{InteractivePhrases.INCORRECT_USER_WORD.value.format(correct_answer=correct_translation, next_word=current_word)}",
                disable_notification=True,
            )

    @staticmethod
    async def stop_quiz(message: Message, state: FSMContext):
        if message.text:
            if message.text.strip().lower() == "/stop_quiz":
                UserActivityProcessor.stopped_quiz(user_id=message.chat.id)
                await state.clear()
                await message.answer(
                    text=InteractivePhrases.STOP_QUIZ.value, disable_notification=True
                )
                return True

        return False

    @staticmethod
    async def start_quiz_with_b1_words(message: Message, state: FSMContext):
        b1_words_from_cache = words_redis_client.get(
            name=WordsCache.B_LEVEL_WORDS.value,
        )
        if b1_words_from_cache:
            file_data_in_bytes = b1_words_from_cache

        else:
            file_path = "constants/files/B1 LEVEL WORDS.xlsx"

            with open(file_path, "rb") as file:
                file_data_in_bytes = file.read()

            words_redis_client.set(
                name=WordsCache.B_LEVEL_WORDS.value,
                value=file_data_in_bytes,
            )
            file_data_in_bytes = words_redis_client.get(
                name=WordsCache.B_LEVEL_WORDS.value,
            )

        await QuizProcessor.process_xlsx_file(
            message=message,
            file_content_type=".xlsx",
            state=state,
            file_data_in_bytes=file_data_in_bytes,
        )

    @staticmethod
    async def start_quiz_with_a2_words(message: Message, state: FSMContext):
        a2_words_from_cache = words_redis_client.get(
            name=WordsCache.A_LEVEL_WORDS.value,
        )
        if a2_words_from_cache:
            file_data_in_bytes = a2_words_from_cache

        else:
            file_path = "constants/files/A2 LEVEL WORDS.xlsx"

            with open(file_path, "rb") as file:
                file_data_in_bytes = file.read()

            words_redis_client.set(
                name=WordsCache.A_LEVEL_WORDS.value,
                value=file_data_in_bytes,
            )

        await QuizProcessor.process_xlsx_file(
            message=message,
            file_content_type=".xlsx",
            state=state,
            file_data_in_bytes=file_data_in_bytes,
        )

    @staticmethod
    async def start_quiz_with_topic_words(message: Message, state: FSMContext):
        UserActivityProcessor.user_play_special_mode(
            user_id=message.chat.id, mode_name="HOUSE WORDS"
        )
        special_words_from_cache = words_redis_client.get(
            name=WordsCache.SPECIAL_WORDS.value,
        )
        if special_words_from_cache:
            file_data_in_bytes = special_words_from_cache

        else:
            file_path = "constants/files/HOUSE WORDS.xlsx"

            with open(file_path, "rb") as file:
                file_data_in_bytes = file.read()

            words_redis_client.set(
                name=WordsCache.SPECIAL_WORDS.value,
                value=file_data_in_bytes,
            )

        await QuizProcessor.process_xlsx_file(
            message=message,
            file_content_type=".xlsx",
            state=state,
            file_data_in_bytes=file_data_in_bytes,
        )

    @staticmethod
    async def start_quiz_with_users_previous_file(message: Message, state: FSMContext):
        await message.answer(
            InteractivePhrases.SUCCESS_GET_PREVIOUS_FILE.value,
            disable_notification=True,
        )

        file_response = None
        try:
            file_response = storage_client.get_object(
                bucket_name=MINIO_BUCKET_NAME, object_name=f"{message.chat.id}.xlsx"
            )
            file_data_in_bytes: bytes = file_response.read()

        except Exception as e:
            await message.answer(
                InteractivePhrases.EMPTY_FILE.value, disable_notification=True
            )
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

    @staticmethod
    async def start_quiz_with_new_file(message: Message, state: FSMContext):
        await state.set_state(AvailableStates.awaiting_file_upload)
