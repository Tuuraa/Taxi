from asyncio import Lock
from aiogram import Dispatcher
from aiogram.types import Message, CallbackQuery
from aiogram.dispatcher import FSMContext


from .LogIn import register_login_handlers
from .Refill import registration_refill_handlers

from bot.env import *
