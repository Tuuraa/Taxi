from aiogram.utils import executor
from aiogram import Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage


from bot.handlers import register_all_handlers
from .env import bot


async def __on_start_up(dp: Dispatcher) -> None:
    register_all_handlers(dp)


def start_bot():
    dp = Dispatcher(bot, storage=MemoryStorage())
    executor.start_polling(dp, skip_updates=True, on_startup=__on_start_up)
