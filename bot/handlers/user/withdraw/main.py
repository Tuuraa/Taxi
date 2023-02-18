from asyncio import Lock
from aiogram import Dispatcher
from aiogram.types import Message

from bot.env import *


lock = Lock()


def register_withdraw_handlers(dp:Dispatcher):
    pass