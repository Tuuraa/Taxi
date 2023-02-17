from asyncio import Lock
from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery

from datetime import datetime

import bot.Database.methods.create as db_create
import bot.Database.methods.get as db_select
import bot.keyboards.inline as inline
import bot.keyboards.reply as reply

from bot.env import *
from bot.states import *

lock = Lock()


async def star_login(message: Message):

    if await db_select.exists_passenger(message.from_user.id) or await db_select.exists_driver( message.from_user.id):
        await message.answer("Добро пожаловать", reply_markup=reply.profile_markup())

    else:
        await message.answer(
            '<b>Taxi bot</b> это крупный бла бла бал,выберите вы пассажир или пользователь',
            reply_markup=inline.check_status_btns(),
            parse_mode='html'
        )


async def driver(callback: CallbackQuery):
    await bot.delete_message(
        callback.from_user.id,
        callback.message.message_id
    )
    await bot.send_message(
        callback.from_user.id,
        'Введите марку вашего автомобиля',
    )

    await DriverFSM.car_mark.set()


async def car_mark(message: Message, state: FSMContext):

    async with state.proxy() as proxy:
        proxy['car_mark'] = message.text

    await bot.send_message(
        message.from_user.id,
        'Введите гос номер вашего автомобиля',
    )
    await DriverFSM.car_numbers.set()


async def driver_number(message: Message, state: FSMContext):

    async with state.proxy() as proxy:
        proxy['car_numbers'] = message.text

    await bot.send_message(
        message.from_user.id,
        'Введите ваше полное имя',
    )
    await DriverFSM.full_name.set()


async def passenger(callback: CallbackQuery):

    await bot.delete_message(
        callback.from_user.id,
        callback.message.message_id
    )

    await bot.send_message(
        callback.from_user.id,
        'Напишите ваше полное имя:\n'
        'Пример: Иванов Иван Иванович'
    )

    await PassengerFSM.full_name.set()


async def full_name_passender(message: Message, state: FSMContext):

    if len(message.text.split(' ')) != 3:
        await message.answer('Неверно введен ФИО!')
        return

    async with state.proxy() as proxy:
        proxy['full_name'] = message.text

    await message.answer(
        'Теперь напишите свой номер телефона'
    )

    await PassengerFSM.phone.set()


async def phone_driver_and_pass(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Неверный номер!")
        return

    if 0 < len(message.text) < 11:
        await message.answer("Неверный номер!")
        return

    async with state.proxy() as proxy:
        await db_create.create_new_user(
            message.from_user.id,
            str(proxy['full_name']).title(),
            message.text,
            message.from_user.username,
            datetime.today()
        )

    await message.answer("Готово")

    await state.reset_state(with_data=True)


def register_login_handlers(dp: Dispatcher):
    dp.register_message_handler(star_login, commands=['start'], state='*')
    dp.register_callback_query_handler(driver, text="driver")
    dp.register_callback_query_handler(passenger, text="passenger")
    dp.register_message_handler(car_mark, state=DriverFSM.car_mark)
    dp.register_message_handler(driver_number, state=DriverFSM.car_numbers)
    dp.register_message_handler(full_name_passender, state=PassengerFSM.full_name)
    dp.register_message_handler(phone_driver_and_pass, state=PassengerFSM.phone)
