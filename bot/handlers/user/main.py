from asyncio import Lock
from datetime import datetime

from aiogram import Dispatcher
from aiogram.types import Message, CallbackQuery, Location, ReplyKeyboardRemove
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


async def star_login(message: Message, state: FSMContext):

    await state.reset_state(with_data=True)

    if await db_select.exists_passenger(message.from_user.id) or await db_select.exists_driver(message.from_user.id):

        user_data = await db_select.type_user(message.from_user.id)
        await message.answer(
            "Добро пожаловать",
            reply_markup=reply.profile_passenger_markup() if user_data == 'passenger' else reply.profile_driver_markup()
        )

    else:
        await message.answer(
            '<b>Taxi bot</b> это крупный бла бла бал,выберите вы пассажир или пользователь',
            reply_markup=inline.check_status_btns(),
            parse_mode='html'
        )


async def profile(message: Message, state: FSMContext):
    await state.reset_state(with_data=True)
    user_data = (await db_select.profile_data(message.from_user.id))

    if user_data[0] == 'pass':
        await message.answer(
            f'🤖 Ваш ID: <b>{user_data[1][0]}</b>\n'
            f'👤 ФИО: <b>{user_data[1][1]}\n</b>'
            f'📱 Телефон: <b>{user_data[1][2]}</b>\n',
            parse_mode='html',
            reply_markup=inline.profile_passenger_btn()
        )
    else:
        await message.answer(
            f'🤖 Ваш ID: <b>{user_data[1][0]}</b>\n'
            f'👤 ФИО: <b>{user_data[1][1]}</b>\n'
            f'📱 Телефон: <b>{user_data[1][2]}</b>\n\n'
            f'🚗 Марка машины: <b>{user_data[1][3]}</b>\n'
            f'🚕 Номер машины: <b>{user_data[1][4]}</b>',
            parse_mode='html',
            reply_markup=inline.profile_driver_btn()
        )


async def current_user_location_handler(message: Message, state: FSMContext):
    location = current_user_location(message)

    async with state.proxy() as proxy:
        proxy['current_location'] = location[0], location[1], location[2]

    await message.answer(
        "А теперь куда хотите поехать.\n"
        "Для этого нажмите на скрепку 📎, и оправьте локацию, куда хотите поехать",
        reply_markup=reply.order_location()
    )

    await UserLocationFSM.next()


async def order_location(message: Message, state: FSMContext):
    location = current_user_location(message)

    async with state.proxy() as proxy:
        proxy['order_location'] = location[0], location[1], location[2]

        location_list = proxy['current_location'][0].address.split(', ')
        republic = ''
        user_data = await db_select.type_user(message.from_user.id)

        for loc in location_list:
            if loc in republics:
                republic = loc
                break

        if not republic:
            await message.answer(
                'В данном регионе этот сервис не работает!!',
                reply_markup=reply.profile_passenger_markup() if user_data == 'passenger' else reply.profile_driver_markup()
            )
            await state.reset_state(with_data=True)
            return

        await message.answer(
            f'Откуда:\n{proxy["current_location"][0]}'
        )

        await message.answer(
            f'Куда:\n{location[0]}'
        )

        first_loc = proxy['current_location'][1], proxy['current_location'][2]
        second_loc = proxy['order_location'][1], proxy['order_location'][2]

        distance = round(distance_btw_two_points(
            current_point=first_loc,
            order_point=second_loc
        ).m, 3)

        await message.answer(
            f'Расстояние состовляет: {distance} м.',
            reply_markup=reply.profile_passenger_markup() if user_data == 'passenger' else reply.profile_driver_markup()
        )

        await db_create.create_order(
            message.from_user.id,
            proxy["current_location"][0],
            location[0],
            distance,
            distance * 1.5,
            republic,
            datetime.now()
        )

    await state.reset_state(with_data=True)


async def order_taxi(message: Message):
    await message.answer(
        'Отправьте локацию, либо пропишите ее вручную',
        reply_markup=reply.set_current_locale()
    )

    await UserLocationFSM.current_location.set()


async def back(message: Message, state: FSMContext):
    await state.reset_state(with_data=True)

    await message.answer(
        'Вернулся',
        reply_markup=reply.profile_passenger_markup()
    )


async def support(message: Message):
    await message.answer(
        'По любым вопросам пишите @bluabitch\n'
        'Ответит в течении часа!'
    )


async def active_orders(message: Message):
    republic = await db_select.republic_by_driver(message.from_user.id)

    orders = await db_select.all_active_orders(republic)

    for order in orders:
        await message.answer(
            f'Заказ №{order[0]}\n\n'
            f'Откуда: {order[1]}\n\n'
            f'Куда: {order[2]}\n\n'
            f'Дистанция: {order[3]} м.\n'
            f'Оплата: {order[4]} руб.\n'
            f'Дата создания заявки: {order[8]}',
            reply_markup=inline.responde_order()
        )


def register_user_handlers(dp: Dispatcher):
    dp.register_message_handler(star_login, commands=['start'], state='*')
    dp.register_message_handler(profile, lambda msg: msg.text == '👤 Профиль', state="*")
    dp.register_message_handler(back, lambda mes: mes.text == '⬅️ Вернуться', state='*')
    dp.register_message_handler(current_user_location_handler, state=UserLocationFSM.current_location,
                                content_types=['location', 'text'])
    dp.register_message_handler(order_location, state=UserLocationFSM.order_location,
                                content_types=['location', 'text'])
    dp.register_message_handler(order_taxi, lambda mes: mes.text == '🚕 Заказать такси')
    dp.register_message_handler(active_orders, lambda mes: mes.text == '🚕 Активные заказы')
    dp.register_message_handler(support, lambda mes: mes.text == 'Техническая поддержка')
    register_login_handlers(dp)
