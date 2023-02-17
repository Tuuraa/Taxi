from asyncio import Lock
from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import Message

import arrow

from bot.env import *
from bot.states import *

lock = Lock()


async def star_login(message: Message):
    await message.answer(
        f'👋 Приветствую Вас в "НАЗВАНИЕ". Для регистрации напишите ваш номер телефона ☎️\n'
        f'Пример: 89294577219'
    )

    await LogInFSM.phone.set()


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
    dp.register_message_handler(star_login, commands=['start'] )
    dp.register_message_handler(phone_login, state=LogInFSM.phone)