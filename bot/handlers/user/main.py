from asyncio import Lock
from aiogram import Dispatcher
from aiogram.types import Message, CallbackQuery, Location
from aiogram.dispatcher import FSMContext

import bot.Database.methods.create as db_create
import bot.Database.methods.get as db_select
import bot.keyboards.inline as inline
import bot.keyboards.reply as reply

from bot.handlers.utils import *

from .login import register_login_handlers
from .refill import register_refill_handlers

from bot.env import *
from ...states import UserLocationFSM


async def current_user_location_handler(message: Message, state: FSMContext):
    location = current_user_location(message)

    async with state.proxy() as proxy:
        proxy['current_location'] = location

    await message.answer(
        "А теперь куда хотите поехать"
    )

    await UserLocationFSM.next()


async def order_location(message: Message, state: FSMContext):
    location = current_user_location(message)

    async with state.proxy() as proxy:
        await message.answer(
            f'Откуда:\n{proxy["current_location"]}'
        )

        await message.answer(
            f'Куда:\n{location}'
        )

    await state.reset_state(with_data=True)


async def order_taxi(message: Message):
    await message.answer(
        'Отправьте локацию, либо пропишите ее вручную',
        reply_markup=reply.set_locale()
    )

    await UserLocationFSM.current_location.set()


async def back(message: Message, state: FSMContext):
    await state.reset_state(with_data=True)

    await message.answer(
        'Вернулся',
        reply_markup=reply.profile_markup()
    )


def register_user_handlers(dp: Dispatcher):
    dp.register_message_handler(back, lambda mes: mes.text == '⬅️ Вернуться', state='*')
    dp.register_message_handler(current_user_location_handler, state=UserLocationFSM.current_location,
                                content_types=['location', 'text'])
    dp.register_message_handler(order_location, state=UserLocationFSM.order_location,
                                content_types=['location', 'text'])
    dp.register_message_handler(order_taxi, lambda mes: mes.text == 'Заказать такси')
    register_login_handlers(dp)
