from asyncio import Lock
from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import Message,CallbackQuery

import arrow

import bot.Database.methods.create as db_create
import bot.Database.methods.get as db_select
import bot.keyboards.inline as inline
from bot.env import *
from bot.states import *

lock = Lock()


async def star_login(message: Message):

    if await db_select.exists_user(message.from_user.id):
        await message.answer("Добро пожаловать")

    else:
        await message.answer(
          '<b>Taxi bot<b> это крупный бла бла бал,выберите вы пассажир или пользователь'

        )



async def phone_login(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Неверный номер!")
        return

    if 0 < len(message.text) < 11:
        await message.answer("Неверный номер!")
        return

    #РЕГЕСТРИРУЙ В БД ЗДЕСЬ АБАЗА

    await message.answer("NICE")

    await state.reset_state(with_data=True)


def register_login_handlers(dp:Dispatcher):
    dp.register_message_handler(star_login, commands=['start'])
    dp.register_callback_query_handler(checking_the_dr_or_pas_BTNS, text='checking_the_dr_or_pas_BTNS')
    dp.register_callback_query_handler(Driver, text= 'Driver')
    dp.register_callback_query_handler(Passenger, text = 'Passenger')
    dp.register_message_handler(phone_login, state=LogInFSM.phone)