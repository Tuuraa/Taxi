from asyncio import Lock
from datetime import datetime

from aiogram import Dispatcher
from aiogram.types import Message, CallbackQuery, Location, ReplyKeyboardRemove
from aiogram.dispatcher import FSMContext

import bot.Database.methods.create as db_create
import bot.Database.methods.get as db_select
import bot.Database.methods.update as db_update

import bot.keyboards.inline as inline
import bot.keyboards.reply as reply

from bot.handlers.utils import *

from .login import register_login_handlers
from .refill import register_refill_handlers
from .withdraw import registration_withdrow_handlers

from bot.env import *
from ...states import UserLocationFSM
from ...states import ChangeRepublicFSM


lock = Lock()


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
            f'📱 Телефон: <b>{user_data[1][2]}</b>\n'
            f'💰 Баланс: <b>{user_data[1][3]}</b> руб.\n',
            parse_mode='html',
            reply_markup=inline.profile_passenger_btn()
        )
    else:
        await message.answer(
            f'🤖 Ваш ID: <b>{user_data[1][0]}</b>\n'
            f'👤 ФИО: <b>{user_data[1][1]}</b>\n'
            f'📱 Телефон: <b>{user_data[1][2]}</b>\n\n'
            f'🚗 Марка машины: <b>{user_data[1][3]}</b>\n'
            f'🚕 Номер машины: <b>{user_data[1][4]}</b>\n'
            f'⛰️ Республика: <b>{user_data[1][5]}</b>\n'
            f'💵 Баланс: <b>{user_data[1][6]}</b> руб.\n',
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

        proxy['distance'] = distance
        proxy['amount'] = distance * 0.6

        await message.answer(
            f'Расстояние состовляет: {distance} м.\n'
            f'Сумма к оплате {distance * 0.6}\n'
            f'Выберите каким образом будете оплачивать',
            reply_markup=inline.pay_order()
        )

        # await db_create.create_order(
        #     message.from_user.id,
        #     proxy["current_location"][0],
        #     location[0],
        #     distance,
        #     distance * 1.5,
        #     republic,
        #     datetime.now()
        # )

    # await state.reset_state(with_data=True)


async def current_del_location_handler(message: Message, state: FSMContext):
    location = current_user_location(message)

    async with state.proxy() as proxy:
        proxy['current_location'] = location[0], location[1], location[2]

    await message.answer(
        "А теперь куда хотите доставить.\n"
        "Для этого нажмите на скрепку 📎, и оправьте локацию, куда хотите поехать",
        reply_markup=reply.order_location()
    )

    await UserLocationFSM.next()


async def del_order_location(message: Message, state: FSMContext):
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
        ).km, 3)

        proxy['distance'] = distance
        proxy['amount'] = distance * 0.6
        proxy['republic'] = republic

        await message.answer(
            f'Расстояние состовляет: {distance} м.\n'
            f'Сумма к оплате {distance * 0.6}\n'
            f'Выберите каким образом будете оплачивать',
            reply_markup=inline.pay_order()
        )

        # await db_create.create_delivery(
        #      message.from_user.id,
        #      proxy["current_location"][0],
        #      location[0],
        #      distance,
        #      distance * 1.5,
        #      republic,
        #      datetime.now()
        #  )

        #await state.reset_state(with_data=True)


async def pay_by_cash(callback: CallbackQuery, state: FSMContext):
    async with state.proxy() as proxy:
        proxy['type_pay'] = 'cash'

        # user_amount = await db_select.balance_by_user(callback.from_user.id)

        #await db_update.add_coefficient(0.5, callback.from_user.id)

        await db_create.create_order(
             callback.from_user.id,
             proxy["current_location"][0],
             proxy["order_location"][0],
             proxy['distance'],
             proxy['amount'],
             proxy['republic'],
             datetime.now(),
             'cash'
         )

        await state.reset_state(with_data=True)


async def pay_by_wallet(callback: CallbackQuery, state: FSMContext):
    async with lock:
        async with state.proxy() as proxy:

            user_balance = await db_select.balance_by_user(callback.from_user.id)

            if user_balance < int(proxy['amount']):
                await bot.send_message(
                    callback.from_user.id,
                    'Недостаточно средств для заказа такси. Необходимо пополнить баланс, либо выбрать другой тип оплаты',
                    reply_markup=inline.not_enough_amount()
                )
                return

            await db_create.create_order(
                callback.from_user.id,
                proxy["current_location"][0],
                proxy["order_location"][0],
                proxy['distance'],
                proxy['amount'],
                proxy['republic'],
                datetime.now(),
                'wallet'
            )

            await state.reset_state(with_data=True)


async def order_del(message: Message):
    await message.answer(
        'Отправьте локацию, либо пропишите ее вручную',
        reply_markup=reply.set_current_locale()
    )
    await UserLocationFSM.current_location.set()


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

    if not orders:
        await message.answer(
            'На данный момент заказов нет'
        )

    for order in orders:
        await message.answer(
            f'Заказ №{order[0]}\n\n'
            f'Откуда: {order[1]}\n\n'
            f'Куда: {order[2]}\n\n'
            f'Дистанция: {order[3]} км.\n'
            f'Оплата: {order[4]} руб.\n'
            f'Дата создания заявки: {order[8]}\n'
            f'Тип оплаты: {order[9]}',
            reply_markup=inline.responde_order(order)
        )


async def responde(callback: CallbackQuery):

    await bot.delete_message(
        callback.from_user.id,
        callback.message.message_id
    )

    order_data = callback.data.split(':')

    user_data = await db_select.information_by_user(int(order_data[1]))
    order_data_by_db = await db_select.information_by_order(int(order_data[2]))
    order_user_data = await db_select.information_by_driver(callback.from_user.id)

    await db_update.change_status_to_order('PROCESSING', order_data[2])

    await bot.send_message(
        int(order_data[1]),
        f'Ваш заказ был принят водителем @{callback.from_user.username}\n\n'
        f'Данные о нем:\n'
        f'Телефон: <b>{order_user_data[5]}</b>\n'
        f'Марка машины: <b>{order_user_data[3]}</b>\n'
        f'Номер машины: <b>{order_user_data[4]}</b>',
        parse_mode='html'
    )

    await bot.send_message(
        callback.from_user.id,
        'Данные о заказе:\n\n'
        f'Откуда: {order_data_by_db[1]}\n\n'
        f'Куда: {order_data_by_db[2]}\n\n'
        f'К оплате: {order_data_by_db[4]}\n'
        f'Телефон пассажира: <b>{user_data[3]}</b>\n'
        f'Ссылка: @{user_data[4]}\n',
        reply_markup=inline.apply_order(user_data[1], order_user_data[1], order_data_by_db[0]),
        parse_mode='html'
    )


async def apply_order(callback: CallbackQuery):

    await bot.delete_message(
        callback.from_user.id,
        callback.message.message_id
    )

    order_data = [int(item) for item in callback.data.split(':')[1:]]

    await db_update.change_status_to_order(order_data[1], 'COMPLETED')




async def change_republics(callback: CallbackQuery):
    await bot.delete_message(
        callback.from_user.id,
        callback.message.message_id
    )
    await bot.send_message(
        callback.from_user.id,
        "Выберите республику:",
        reply_markup=reply.all_republics()
    )

    await ChangeRepublicFSM.republic.set()


async def new_republic(message: Message, state: FSMContext):

    await db_update.change_region(
        message.from_user.id,
        message.text
    )

    await message.answer(
        'Республика успешно изменена',
        reply_markup=reply.profile_driver_markup()
    )

    await state.reset_state(with_data=True)


def register_user_handlers(dp: Dispatcher):
    dp.register_message_handler(star_login, commands=['start'], state='*')
    dp.register_message_handler(profile, lambda msg: msg.text == '👤 Профиль', state="*")
    dp.register_message_handler(back, lambda mes: mes.text == '⬅️ Вернуться', state='*')
    dp.register_callback_query_handler(change_republics, text='change_region')
    dp.register_message_handler(new_republic, state=ChangeRepublicFSM.republic)
    dp.register_message_handler(current_user_location_handler, state=UserLocationFSM.current_location,
                                content_types=['location', 'text'])
    dp.register_message_handler(order_location, state=UserLocationFSM.order_location,
                                content_types=['location', 'text'])
    dp.register_message_handler(current_del_location_handler,  state=UserLocationFSM.current_location,
                                content_types=['location', 'text'])
    dp.register_message_handler(del_order_location, state=UserLocationFSM.order_location,
                                content_types=['location', 'text'])
    dp.register_message_handler(order_taxi, lambda mes: mes.text == '🚕 Заказать такси')
    dp.register_message_handler(order_del, lambda mes: mes.text == 'Заказать доставку')
    dp.register_message_handler(active_orders, lambda mes: mes.text == '🚕 Активные заказы')
    dp.register_message_handler(support, lambda mes: mes.text == '⚙️ Техническая поддержка')
    dp.register_callback_query_handler(pay_by_cash, text='pay_by_cash', state=UserLocationFSM.type_pay)
    dp.register_callback_query_handler(pay_by_wallet, text='pay_by_wallet', state=UserLocationFSM.type_pay)
    dp.register_callback_query_handler(responde, inline.cb_data.filter(data='responde'))
    dp.register_callback_query_handler(apply_order, inline.cb_apply.filter(data='apply_order'))
    register_login_handlers(dp)
    registration_withdrow_handlers(dp)
    register_refill_handlers(dp)
