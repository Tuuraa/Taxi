from asyncio import Lock
from aiogram import Dispatcher
from aiogram.types import Message, CallbackQuery
from aiogram.dispatcher import FSMContext


from .login import register_login_handlers
from .refill import register_refill_handlers

from bot.env import *


def register_user_handlers(dp: Dispatcher):
    register_login_handlers(dp)
