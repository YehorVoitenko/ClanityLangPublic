import asyncio
import random
from datetime import datetime

import pytz
from aiogram import F
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, FSInputFile, CallbackQuery

from api.routers.subscriptions.schemas import GetSubscriptionLinkRequest
from bot.processors.promocode_processor import PromocodeProcessor
from bot.processors.subscription_processor import SubscriptionProcessor
from bot.processors.user_processor import UserProcessor
from constants.constants import (
    PATH_TO_INSTRUCTION_FILE,
    INSTRUCTION_FILE_NAME,
    SIMPLE_SUB_COST,
    START_SUB_COST,
    PRO_SUB_COST,
)
from constants.enums import StateKeys
from constants.phrases import (
    InteractivePhrases,
    SIMPLE_SUB_DESCRIPTION,
    START_SUB_DESCRIPTION,
    PRO_SUB_DESCRIPTION,
    MOTIVATION_PHRASES_FOR_MISTAKES,
)
from models import UserSubscriptionLevels
from processors.bot_processors import QuizProcessor
from processors.storage_service_processor import StorageServiceProcessor
from services.background_task_service.celery_methods import send_user_info_about_update
from services.bot_services.bot_initializer import dispatcher
from services.bot_services.bot_initializer import initialize_bot
from services.bot_services.buttons import ButtonOrchestrator
from services.bot_services.states import AvailableStates
from services.database import init_tables


@dispatcher.message(CommandStart())
async def start_cmd(message: Message):
    if message.from_user.is_bot:
        return

    await UserProcessor.create_user_if_not_exists(message=message)
    await UserProcessor.add_user_session(message=message)
    await SubscriptionProcessor.check_purchase_status(message=message)

    user_instance = await UserProcessor.get_user_by_id(message=message)

    await message.answer(
        text=InteractivePhrases.WELCOME_MESSAGE.value,
        reply_markup=ButtonOrchestrator.set_buttons_for_quiz_starting(
            level=user_instance.subscription_level
        ),
    )
    return


@dispatcher.message(Command("instruction"))
async def instruction_cmd(message: Message):
    if message.from_user.is_bot:
        return

    await message.answer(
        text=InteractivePhrases.INSTRUCTION.value
    )
    return


@dispatcher.message(Command("help"))
async def help_cmd(message: Message):
    if message.from_user.is_bot:
        return

    await message.answer(
        text=InteractivePhrases.HELP.value,
    )
    return


@dispatcher.message(Command("add_promocode"))
async def add_promocode_cmd(message: Message, state: FSMContext):
    if message.from_user.is_bot:
        return

    await message.answer(
        text=InteractivePhrases.ADD_PROMOCODE.value, parse_mode="Markdown"
    )
    await state.set_state(AvailableStates.waiting_for_promocode)


@dispatcher.message(AvailableStates.waiting_for_promocode)
async def handle_promocode_input(message: Message, state: FSMContext):
    if message.from_user.is_bot:
        return

    response = await PromocodeProcessor.process_user_promocode(
        promocode=message.text.strip(), message=message
    )

    await message.answer(response)
    await state.clear()


@dispatcher.callback_query(F.data == "process_simple_subscription")
async def process_simple_subscription(callback):
    purchase_link = await SubscriptionProcessor.get_subscription_link(
        request=GetSubscriptionLinkRequest(
            user_id=callback.message.chat.id,
            subscription_level=UserSubscriptionLevels.SIMPLE,
            cost_in_dollar=SIMPLE_SUB_COST,
        )
    )

    await callback.message.answer(
        f"{SIMPLE_SUB_DESCRIPTION} \n\n"
        f'👉<b><a href="{purchase_link}">Посилання на оплату підписки (через MonoPay)</a></b>👈'
    )


@dispatcher.callback_query(F.data == "process_start_subscription")
async def process_start_subscription(callback):
    purchase_link = await SubscriptionProcessor.get_subscription_link(
        request=GetSubscriptionLinkRequest(
            user_id=callback.message.chat.id,
            subscription_level=UserSubscriptionLevels.START,
            cost_in_dollar=START_SUB_COST,
        )
    )
    await callback.message.answer(
        f"{START_SUB_DESCRIPTION} \n\n"
        f'👉<b><a href="{purchase_link}">Посилання на оплату підписки (через MonoPay)</a></b>👈'
    )


@dispatcher.callback_query(F.data == "process_pro_subscription")
async def process_pro_subscription(callback):
    purchase_link = await SubscriptionProcessor.get_subscription_link(
        request=GetSubscriptionLinkRequest(
            user_id=callback.message.chat.id,
            subscription_level=UserSubscriptionLevels.PRO,
            cost_in_dollar=PRO_SUB_COST,
        )
    )
    await callback.message.answer(
        f"{PRO_SUB_DESCRIPTION} \n\n"
        f'👉<b><a href="{purchase_link}">Посилання на оплату підписки (через MonoPay)</a></b>👈'
    )


@dispatcher.callback_query(F.data == "start_quiz_with_new_file")
async def start_quiz_with_new_file(callback, state: FSMContext):
    await callback.message.answer(
        text=InteractivePhrases.FILE_SEND_INSTRUCTION.value, parse_mode="Markdown"
    )

    sample_file = FSInputFile(
        path=PATH_TO_INSTRUCTION_FILE, filename=INSTRUCTION_FILE_NAME
    )
    await callback.message.answer_document(document=sample_file)

    result = await QuizProcessor.start_quiz_with_new_file(
        message=callback.message, state=state
    )

    if result is None:
        return


@dispatcher.callback_query(F.data == "start_quiz_with_users_previous_file")
async def start_quiz_with_users_previous_file(callback, state: FSMContext):
    result = await QuizProcessor.start_quiz_with_users_previous_file(
        message=callback.message, state=state
    )

    if result is None:
        return


@dispatcher.callback_query(F.data == "start_quiz_with_a2_words")
async def start_quiz_with_a2_words(callback, state: FSMContext):
    result = await QuizProcessor.start_quiz_with_a2_words(
        message=callback.message, state=state
    )

    if result is None:
        return


@dispatcher.callback_query(F.data == "start_quiz_with_b1_words")
async def start_quiz_with_b1_words(callback, state: FSMContext):
    result = await QuizProcessor.start_quiz_with_b1_words(
        message=callback.message, state=state
    )

    if result is None:
        return


@dispatcher.callback_query(F.data == "start_quiz_with_travel_words")
async def start_quiz_with_travel_words(callback, state: FSMContext):
    result = await QuizProcessor.start_quiz_with_travel_words(
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


def mask_word(word: str) -> str:
    if len(word) <= 2:
        return word

    masked_word = ""
    for word_part in word.split(" "):
        for index, letter in enumerate(word_part, start=1):
            if letter:
                masked_word += f"||{letter}||" if index % 2 == 0 else letter
                continue

            masked_word += letter

    return masked_word


@dispatcher.callback_query(F.data == "get_hint")
async def handle_get_hint(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    word = data.get(StateKeys.CURRENT_TRANSLATION.value, "")
    await callback.message.answer(
        text=f"👀👀👀 {mask_word(word=word)}", parse_mode=ParseMode.MARKDOWN_V2
    )
    await callback.answer()


@dispatcher.callback_query(F.data == "skip_word")
async def handle_skip_word(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    quiz_data: dict = data.get(StateKeys.QUIZ_DATA.value, {})
    current_word: str = data.get(StateKeys.CURRENT_WORD.value)

    if not quiz_data or current_word not in quiz_data:
        await callback.message.answer(InteractivePhrases.FINISH_QUIZ.value)
        await state.clear()
        return

    correct_answer = quiz_data.pop(current_word)

    if not quiz_data:
        await callback.message.answer(InteractivePhrases.FINISH_QUIZ.value)
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

    await callback.message.answer(
        text=f"{random.choice(MOTIVATION_PHRASES_FOR_MISTAKES)}\n\n"
             + InteractivePhrases.PASSED_USER_WORD.value.format(
            correct_answer=correct_answer,
            next_word=next_word,
        ),
        reply_markup=ButtonOrchestrator.generate_word_buttons(),
    )
    await callback.answer()


if __name__ == "__main__":
    init_tables()
    StorageServiceProcessor.init_minio_bucket()
    ukraine_tz = pytz.timezone("Europe/Kyiv")

    local_run_at = ukraine_tz.localize(datetime(2025, 5, 29, 17, 00))

    run_at_utc = local_run_at.astimezone(pytz.UTC)
    send_user_info_about_update.apply_async(eta=run_at_utc)
    asyncio.run(initialize_bot())
