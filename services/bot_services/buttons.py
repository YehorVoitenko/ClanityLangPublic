from aiogram import Bot
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, BotCommand

from constants.constants import SIMPLE_SUB_COST, START_SUB_COST, PRO_SUB_COST
from models import UserSubscriptionLevels


class ButtonOrchestrator:
    @classmethod
    def set_buttons_for_quiz_starting(cls, level: UserSubscriptionLevels = UserSubscriptionLevels.PRO):
        NEED_SUB = '(need sub 💸)'
        STATUS_OK = ''

        button_list = [
            [InlineKeyboardButton(
                text=f"My new files {NEED_SUB if level == UserSubscriptionLevels.NON_SUBSCRIPTION else STATUS_OK}",
                callback_data='start_quiz_with_new_file')],

            [InlineKeyboardButton(
                text=f"Use my previous file {NEED_SUB if level == UserSubscriptionLevels.NON_SUBSCRIPTION else STATUS_OK}",
                callback_data='start_quiz_with_users_previous_file')],

            [InlineKeyboardButton(
                text=f"Use A2 words {STATUS_OK if level in [UserSubscriptionLevels.START, UserSubscriptionLevels.PRO, UserSubscriptionLevels.FREE_TERM] else NEED_SUB}",
                callback_data='start_quiz_with_a2_words')],

            [InlineKeyboardButton(
                text=f"Use B1 words {STATUS_OK if level in [UserSubscriptionLevels.PRO, UserSubscriptionLevels.FREE_TERM] else NEED_SUB}",
                callback_data='start_quiz_with_b1_words')],

        ]
        return InlineKeyboardMarkup(inline_keyboard=button_list)

    @classmethod
    def set_subscription_buttons(cls):
        button_list = [
            [InlineKeyboardButton(text=f"1️⃣ Simple sub [info]   ({SIMPLE_SUB_COST}$)",
                                  callback_data='process_simple_subscription')],
            [InlineKeyboardButton(text=f"2️⃣ Start sub [info]    ({START_SUB_COST}$)",
                                  callback_data='process_start_subscription')],
            [InlineKeyboardButton(text=f"3️⃣ Pro sub [info]    ({PRO_SUB_COST}$)",
                                  callback_data='process_pro_subscription')],
        ]
        return InlineKeyboardMarkup(inline_keyboard=button_list)

    @classmethod
    async def set_menu_buttons(cls, bot: Bot):
        commands = [
            BotCommand(command="start", description="▶️ Start quiz"),
            BotCommand(command="instruction", description="📖 Instruction"),
            BotCommand(command="stop_quiz", description="🛑 Stop quiz"),
        ]
        await bot.set_my_commands(commands)

    @classmethod
    def generate_word_buttons(cls):
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="💡 Hint", callback_data="get_hint"),
                    InlineKeyboardButton(text="➡️ Pass", callback_data="skip_word"),
                ]
            ]
        )
