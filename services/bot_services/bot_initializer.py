from aiogram import Bot
from aiogram import Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from config.bot_config import TOKEN
from services.bot_services.buttons import ButtonOrchestrator

dispatcher = Dispatcher(storage=MemoryStorage())
bot = Bot(
    token=TOKEN,
    default=DefaultBotProperties(
        parse_mode=ParseMode.HTML
    )
)


async def initialize_bot() -> None:
    await ButtonOrchestrator.set_menu_buttons(bot=bot)

    await dispatcher.start_polling(bot)
