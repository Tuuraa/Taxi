from asyncio import Lock
from aiogram import Dispatcher
from aiogram.types import Message, CallbackGame
from aiogram.dispatcher import FSMContext
from datetime import datetime, timezone

import arrow


import bot.Database.methods.create as db_create
import bot.Database.methods.get as db_select
import bot.keyboards.inline as inline
import bot.keyboards.reply as reply


lock = Lock()


def register_refill_handlers(dp:Dispatcher):
    pass
