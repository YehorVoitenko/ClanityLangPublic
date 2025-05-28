from aiogram import Bot
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, BotCommand

from constants.constants import SIMPLE_SUB_COST, START_SUB_COST, PRO_SUB_COST
from models import UserSubscriptionLevels


class ButtonOrchestrator:
    @classmethod
    def set_buttons_for_quiz_starting(
            cls, level: UserSubscriptionLevels = UserSubscriptionLevels.PRO
    ):
        NEED_SUB = "(💸)"
        STATUS_OK = ""

        button_list = [
            [
                InlineKeyboardButton(
                    text=f"Додати свій файл {NEED_SUB if level == UserSubscriptionLevels.NON_SUBSCRIPTION else STATUS_OK}",
                    callback_data="start_quiz_with_new_file",
                )
            ],
            [
                InlineKeyboardButton(
                    text=f"Попередні слова {NEED_SUB if level == UserSubscriptionLevels.NON_SUBSCRIPTION else STATUS_OK}",
                    callback_data="start_quiz_with_users_previous_file",
                )
            ],
            [
                InlineKeyboardButton(
                    text=f"Рівень слів A1–A2 🇺🇸🇺🇦 {STATUS_OK if level in [UserSubscriptionLevels.START, UserSubscriptionLevels.PRO, UserSubscriptionLevels.FREE_TERM, UserSubscriptionLevels.PROMOCODE] else NEED_SUB}",
                    callback_data="start_quiz_with_a2_words",
                )
            ],
            [
                InlineKeyboardButton(
                    text=f"Рівень слів B1–B2 🇺🇸🇺🇦 {STATUS_OK if level in [UserSubscriptionLevels.PRO, UserSubscriptionLevels.FREE_TERM, UserSubscriptionLevels.PROMOCODE] else NEED_SUB}",
                    callback_data="start_quiz_with_b1_words",
                )
            ],
            [
                InlineKeyboardButton(
                    text=f"СЛОВА ДЛЯ ПОДОРОЖЕЙ ✈️ {STATUS_OK if level in [UserSubscriptionLevels.START, UserSubscriptionLevels.PRO, UserSubscriptionLevels.FREE_TERM, UserSubscriptionLevels.PROMOCODE] else NEED_SUB}",
                    callback_data="start_quiz_with_travel_words",
                )
            ],
        ]
        return InlineKeyboardMarkup(inline_keyboard=button_list)

    @classmethod
    def set_subscription_buttons(cls):
        button_list = [
            [
                InlineKeyboardButton(
                    text=f"1️⃣ Підписка 'Simple' [info]   ({SIMPLE_SUB_COST}$)",
                    callback_data="process_simple_subscription",
                )
            ],
            [
                InlineKeyboardButton(
                    text=f"2️⃣ Підписка 'Start' [info]    ({START_SUB_COST}$)",
                    callback_data="process_start_subscription",
                )
            ],
            [
                InlineKeyboardButton(
                    text=f"3️⃣ Підписка 'Pro' [info]    ({PRO_SUB_COST}$)",
                    callback_data="process_pro_subscription",
                )
            ],
        ]
        return InlineKeyboardMarkup(inline_keyboard=button_list)

    @classmethod
    async def set_menu_buttons(cls, bot: Bot):
        commands = [
            BotCommand(command="start", description="▶️ Почати гру"),
            BotCommand(command="instruction", description="📖 Правила"),
            BotCommand(command="help", description="🙏 Допомога"),
            BotCommand(command="add_promocode", description="🔥 Додати промокод"),
            BotCommand(command="stop_quiz", description="🛑 Зупинити гру"),
        ]
        await bot.set_my_commands(commands)

    @classmethod
    def generate_word_buttons(cls):
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="💡 Підказка", callback_data="get_hint"),
                    InlineKeyboardButton(
                        text="➡️ Пропустити", callback_data="skip_word"
                    ),
                ]
            ]
        )
