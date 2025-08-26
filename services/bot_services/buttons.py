from aiogram import Bot
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, BotCommand

from constants.constants import PRO_SUB_COST


class ButtonOrchestrator:
    @classmethod
    def set_buttons_for_quiz_starting(cls):
        button_list = [
            [
                InlineKeyboardButton(
                    text=f"Додати свій файл",
                    callback_data="start_quiz_with_new_file",
                )
            ],
            [
                InlineKeyboardButton(
                    text=f"Попередні слова",
                    callback_data="start_quiz_with_users_previous_file",
                )
            ],
            [
                InlineKeyboardButton(
                    text=f"Рівень слів A1–A2 🇺🇸🇺🇦",
                    callback_data="start_quiz_with_a2_words",
                )
            ],
            [
                InlineKeyboardButton(
                    text=f"Рівень слів B1–B2 🇺🇸🇺🇦",
                    callback_data="start_quiz_with_b1_words",
                )
            ],
            [
                InlineKeyboardButton(
                    text=f"СЛОВА ДЛЯ ПОБУТУ 🏡",
                    callback_data="start_quiz_with_topic_words",
                )
            ],
        ]
        return InlineKeyboardMarkup(inline_keyboard=button_list)

    @classmethod
    def set_subscription_buttons(cls):
        button_list = [
            [
                InlineKeyboardButton(
                    text=f" Підписка 'Pro' [info]    ({PRO_SUB_COST}$)",
                    callback_data="process_pro_subscription",
                )
            ],
        ]
        return InlineKeyboardMarkup(inline_keyboard=button_list)

    @classmethod
    async def set_menu_buttons(cls, bot: Bot):
        commands = [
            BotCommand(command="start", description="▶️ Почати гру"),
            BotCommand(command="stop_quiz", description="🛑 Зупинити гру"),
            BotCommand(command="instruction", description="📖 Правила"),
            BotCommand(command="help", description="🤥 Знайшов проблему.."),
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
                    InlineKeyboardButton(
                        text="🎙️ Послухати", callback_data="listen_word"
                    ),
                ]
            ]
        )
