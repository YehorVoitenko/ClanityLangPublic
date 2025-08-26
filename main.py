import asyncio
import random

from aiogram import F
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, FSInputFile, CallbackQuery

from bot.processors.user_processor import UserProcessor
from constants.constants import (
    PATH_TO_INSTRUCTION_FILE,
    INSTRUCTION_FILE_NAME,
)
from constants.enums import StateKeys
from constants.phrases import (
    InteractivePhrases,
    MOTIVATION_PHRASES_FOR_MISTAKES,
)
from processors.bot_processors import QuizProcessor
from processors.storage_service_processor import StorageServiceProcessor
from processors.user_activity_processor import UserActivityProcessor
from services.bot_services.auidio import (
    normalize_word_for_pronunciation,
    synth_and_send_voice,
)
from services.bot_services.bot_initializer import dispatcher
from services.bot_services.bot_initializer import initialize_bot
from services.bot_services.buttons import ButtonOrchestrator
from services.bot_services.files import upload_files_to_cache
from services.bot_services.states import AvailableStates
from services.database import init_tables
from services.elastic_service.elastic_service import (
    create_elastic_indexes_if_not_exists,
)
from services.gpt_service.client import ask_gpt_async
from services.gpt_service.prompts import CREATE_SENTENCE_PROMPT, DESCRIBE_WORD_PROMPT
from services.utils import escape_markdown_v2, mask_word


@dispatcher.message(CommandStart())
async def start_cmd(message: Message):
    if message.from_user.is_bot:
        return

    await UserProcessor.create_user_if_not_exists(message=message)
    await UserProcessor.add_user_session(message=message)

    await message.answer(
        text=InteractivePhrases.WELCOME_MESSAGE.value,
        reply_markup=ButtonOrchestrator.set_buttons_for_quiz_starting(),
        disable_notification=True,
    )
    return


@dispatcher.message(Command("instruction"))
async def instruction_cmd(message: Message):
    UserActivityProcessor.user_tap_get_instructions_button(message.chat.id)

    if message.from_user.is_bot:
        return

    await message.answer(
        text=InteractivePhrases.INSTRUCTION.value, disable_notification=True
    )
    return


@dispatcher.message(Command("help"))
async def help_cmd(message: Message):
    if message.from_user.is_bot:
        return

    UserActivityProcessor.ask_for_help(user_id=message.chat.id)

    await message.answer(text=InteractivePhrases.HELP.value, disable_notification=True)
    return


@dispatcher.callback_query(F.data == "start_quiz_with_new_file")
async def start_quiz_with_new_file(callback, state: FSMContext):
    UserActivityProcessor.user_tap_add_file_button(callback.message.chat.id)

    await callback.message.answer(
        text=InteractivePhrases.FILE_SEND_INSTRUCTION.value,
        parse_mode="Markdown",
        disable_notification=True,
    )

    sample_file = FSInputFile(
        path=PATH_TO_INSTRUCTION_FILE, filename=INSTRUCTION_FILE_NAME
    )
    await callback.message.answer_document(
        document=sample_file, disable_notification=True
    )

    result = await QuizProcessor.start_quiz_with_new_file(
        message=callback.message, state=state
    )

    if result is None:
        return


@dispatcher.callback_query(F.data == "start_quiz_with_users_previous_file")
async def start_quiz_with_users_previous_file(callback, state: FSMContext):
    UserActivityProcessor.user_used_last_file(callback.message.chat.id)

    result = await QuizProcessor.start_quiz_with_users_previous_file(
        message=callback.message, state=state
    )

    if result is None:
        return


@dispatcher.callback_query(F.data == "start_quiz_with_a2_words")
async def start_quiz_with_a2_words(callback, state: FSMContext):
    UserActivityProcessor.user_play_a1_a2_level(callback.message.chat.id)

    result = await QuizProcessor.start_quiz_with_a2_words(
        message=callback.message, state=state
    )

    if result is None:
        return


@dispatcher.callback_query(F.data == "start_quiz_with_b1_words")
async def start_quiz_with_b1_words(callback, state: FSMContext):
    UserActivityProcessor.user_play_b1_b2_level(callback.message.chat.id)

    result = await QuizProcessor.start_quiz_with_b1_words(
        message=callback.message, state=state
    )

    if result is None:
        return


@dispatcher.callback_query(F.data == "start_quiz_with_topic_words")
async def start_quiz_with_topic_words(callback, state: FSMContext):
    result = await QuizProcessor.start_quiz_with_topic_words(
        message=callback.message, state=state
    )

    if result is None:
        return


@dispatcher.message(AvailableStates.awaiting_file_upload, F.document)
async def handle_new_file_from_user(message: Message, state: FSMContext):
    await QuizProcessor.process_user_new_file(message=message, state=state)


@dispatcher.message(AvailableStates.awaiting_previous_file_upload)
async def handle_previous_user_file(message: Message, state: FSMContext):
    await QuizProcessor.process_previous_user_file(message=message, state=state)


@dispatcher.message(AvailableStates.process_user_word_answer)
async def handle_quiz_answer_or_stop(message: Message, state: FSMContext):
    if await QuizProcessor.stop_quiz(message=message, state=state):
        return

    await QuizProcessor.process_user_answer(message=message, state=state)


@dispatcher.callback_query(F.data == "get_hint")
async def handle_get_hint(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    current_word = data.get(StateKeys.CURRENT_WORD.value, "")
    translation = data.get(StateKeys.CURRENT_TRANSLATION.value, "")

    UserActivityProcessor.user_used_hint(
        callback.message.chat.id, original_word=current_word
    )

    hint_text = await ask_gpt_async(
        prompt=DESCRIBE_WORD_PROMPT(current_word=current_word, translation=translation)
    )

    safe_hint_text = escape_markdown_v2(text=hint_text)

    await callback.message.edit_text(
        text=(
            f"Підказка до слова *{escape_markdown_v2(current_word)}*:\n\n"
            f"> _{safe_hint_text}_\n\n\n\n"
            f"👀👀👀 {mask_word(word=translation)}\n\n"
        ),
        parse_mode="MarkdownV2",
        reply_markup=ButtonOrchestrator.generate_word_buttons(),
    )
    await callback.answer()


@dispatcher.callback_query(F.data == "listen_word")
async def handle_listen_word(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    current_word = data.get(StateKeys.CURRENT_WORD.value, "")
    translation = data.get(StateKeys.CURRENT_TRANSLATION.value, "")
    UserActivityProcessor.user_listened_word(
        callback.message.chat.id, original_word=current_word
    )

    sentence_example = await ask_gpt_async(
        prompt=CREATE_SENTENCE_PROMPT(
            current_word=current_word, translation=translation
        )
    )
    sentence = normalize_word_for_pronunciation(word=sentence_example)
    await synth_and_send_voice(message=callback.message, text=sentence)


@dispatcher.callback_query(F.data == "skip_word")
async def handle_skip_word(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    quiz_data: dict = data.get(StateKeys.QUIZ_DATA.value, {})
    current_word: str = data.get(StateKeys.CURRENT_WORD.value)
    UserActivityProcessor.user_passed_word(
        callback.message.chat.id, original_word=current_word
    )

    if not quiz_data or current_word not in quiz_data:
        try:
            await callback.message.edit_text(
                InteractivePhrases.FINISH_QUIZ.value, reply_markup=None
            )
        except TelegramBadRequest as e:
            if "message is not modified" not in str(e).lower():
                raise
        await state.clear()
        await callback.answer()
        return

    correct_answer = quiz_data.pop(current_word)

    if not quiz_data:
        try:
            await callback.message.edit_text(
                InteractivePhrases.FINISH_QUIZ.value, reply_markup=None
            )
        except TelegramBadRequest as e:
            if "message is not modified" not in str(e).lower():
                raise
        await state.clear()
        await callback.answer()
        return

    next_word = random.choice(list(quiz_data.keys()))
    await state.set_data(
        {
            StateKeys.QUIZ_DATA.value: quiz_data,
            StateKeys.CURRENT_WORD.value: next_word,
            StateKeys.CURRENT_TRANSLATION.value: quiz_data[next_word],
        }
    )

    text = (
            f"{random.choice(MOTIVATION_PHRASES_FOR_MISTAKES)}\n\n"
            + InteractivePhrases.PASSED_USER_WORD.value.format(
            correct_answer=correct_answer,
            next_word=next_word,
    )
    )

    try:
        await callback.message.edit_text(
            text=text,
            reply_markup=ButtonOrchestrator.generate_word_buttons(),
        )
    except TelegramBadRequest as e:
        if "message is not modified" not in str(e).lower():
            raise

    await callback.answer()


if __name__ == "__main__":
    # docker exec -it clanitylang-postgres-1 psql -U <username> <database_user>
    upload_files_to_cache()
    init_tables()
    create_elastic_indexes_if_not_exists()
    StorageServiceProcessor.init_minio_bucket()

    asyncio.run(initialize_bot())
