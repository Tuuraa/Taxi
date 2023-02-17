from asyncio import Lock
from aiogram import Dispatcher
from aiogram.types import Message

import arrow

from bot.env import *


lock = Lock()


def register_admin_handlers(dp:Dispatcher):
    pass