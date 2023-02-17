from asyncio import Lock
from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery

import arrow

import bot.Database.methods.create as db_create
import bot.Database.methods.get as db_select
import bot.keyboards.inline as inline
import bot.keyboards.reply as reply

from bot.env import *
from bot.states import *

lock = Lock()


async def star_login(message: Message):

    #if await db_select.exists_user(message.from_user.id):
    await message.answer("Добро пожаловать", reply_markup=reply.profile_markup())

    # else:
    #     await message.answer(
    #         '<b>Taxi bot<b> это крупный бла бла бал,выберите вы пассажир или пользователь',
    #         reply_markup=inline.check_status_btns()
    #     )
    #
    # await DriverFSM.phone.set()


async def driver(callback: CallbackQuery):
    await bot.delete_message(
        callback.from_user.id,
        callback.message.message_id
    )
    await bot.send_message(
        callback.from_user.id,
        'Введите марку вашего автомобиля',
    )
#проверка на
    await DriverFSM.car_mark.set()


async def car_mark(message: Message, state: FSMContext):
    await bot.send_message(
        message.from_user.id,
        'Введите гос номер вашего автомобиля',
    )
    await DriverFSM.car_numbers.set()


async def driver_name(message:Message, state:FSMContext):
    await bot.send_message(
        message.from_user.id,
        'Введите ваше полное имя',
    )
    await DriverFSM.full_name.set()

async def passenger(callback: CallbackQuery):
    pass


async def phone_driver_and_pass(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Неверный номер!")
        return

    if 0 < len(message.text) < 11:
        await message.answer("Неверный номер!")
        return

    #РЕГЕСТРИРУЙ В БД ЗДЕСЬ АБАЗА

    await message.answer("NICE")

    await state.reset_state(with_data=True)


def register_login_handlers(dp: Dispatcher):
    dp.register_message_handler(star_login, commands=['start'])
    dp.register_callback_query_handler(driver, text="driver")
    dp.register_callback_query_handler(passenger, text="passenger")
    dp.register_message_handler(car_mark, state=DriverFSM.car_mark)
    dp.register_message_handler(phone_driver_and_pass, state=DriverFSM.phone)
