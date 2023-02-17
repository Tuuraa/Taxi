from asyncio import Lock
from aiogram import Dispatcher
from aiogram.types import Message


import arrow


from bot.env import *


lock = Lock()


async def star_login(message: Message):





def register_login_handlers(dp:Dispatcher):
    dp.register_message_handler(star_login,commands=['start'] )