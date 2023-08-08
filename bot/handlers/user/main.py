from asyncio import Lock

from aiogram import Dispatcher
from aiogram.types import Message, CallbackQuery
from aiogram.dispatcher import FSMContext

import bot.Database.methods.get as db_select

import bot.keyboards.reply as reply

from bot.handlers.utils import *

from .login import register_login_handlers
from .refill import register_refill_handlers
from .withdraw import registration_withdrow_handlers
from .register_order import register_create_order_handlers
from .order_tools import register_order_tools_handlers

from .count_down import *

from bot.env import *
from ...states import *


lock = Lock()


async def star_login(message: Message, state: FSMContext):

    await state.reset_state(with_data=True)

    if await db_select.exists_passenger(message.from_user.id) and message.from_user.id in admins:
        await message.answer(
            'Добро пожаловать',
            reply_markup=reply.admin_panel_btns()
        )

    elif await db_select.exists_passenger(message.from_user.id) or await db_select.exists_driver(message.from_user.id):

        user_data = await db_select.type_user(message.from_user.id)
        await message.answer(
            "Добро пожаловать",
            reply_markup=reply.profile_passenger_markup() if user_data == 'passenger' else reply.profile_driver_markup()
        )

    else:
        await message.answer(
            f'<b>Transfer</b> такси-бот в телеграмме направленный '
            f'на то, чтобы вы быстро, удобно, а главное дешево доехали в нужное вам место.\n'
            f'<b>Transfer</b> выгоден не только для пользователей, но и для водителей, из-за отсутствия '
            f'какого либо налога на них.',
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
            f'💰 Баланс: <b>{user_data[1][3]}</b> руб'
            f'<a href=\"https://i.ibb.co/9sfJy3J/image.png\">.</a>',
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
            f'💵 Баланс: <b>{user_data[1][6]}</b> руб\n'
            f'<a href=\"https://i.ibb.co/9sfJy3J/image.png\">.</a>',
            parse_mode='html',
            reply_markup=inline.profile_driver_btn()
        )


async def change_order(message: Message, state: FSMContext):

    async with state.proxy() as proxy:

        if proxy['changed'] == 'Изменить кол_во пассажиров':
            await db_update.update_name_from_driver(message.text, int(proxy['user_id']))
        elif proxy['changed'] == 'Надичие багажа':
            await db_update.update_balance_from_driver(message.text, int(proxy['user_id']))
            await message.answer(
                'Данные успешно обновлены',
                reply_markup=reply.profile_passenger_markup()
            )

        await state.reset_state(with_data=True)


async def order_delivery(message: Message, state: FSMContext):

    await state.reset_state(with_data=True)

    await message.answer(
        'Отправьте локацию, либо пропишите ее вручную',
        reply_markup=reply.set_current_locale()
    )

    await DeliveryFSM.current_delivery_location.set()


async def order_taxi(message: Message, state: FSMContext):
    user_balance = await db_select.balance_by_user(message.from_user.id)

    if await db_select.check_wrong_status_to_cancel(message.from_user.id):
        await message.answer("У вас уже есть активные заказы")
        return

    elif user_balance < 0:
        await message.answer('Не достаточно средств для заказа такси')
        return
    else:
        await message.answer(
            "Какое количество пассажиров поедет.\n"
            "Обратите внимание количество пассажиров должно быть точно указано"
        )

    await state.reset_state(with_data=True)

    await UserLocationFSM.numbers_of_users.set()


async def back(message: Message, state: FSMContext):
    await state.reset_state(with_data=True)

    await message.answer(
        'Вернулся',
        reply_markup=reply.profile_passenger_markup()
    )


async def support(message: Message, state: FSMContext):

    await state.reset_state(with_data=True)

    await message.answer(
        f'По любым вопросам пишите {admin_link}\n'
        'Ответит в течении часа!'
    )


async def active_orders(message: Message, state: FSMContext):

    await state.reset_state(with_data=True)

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
            f'Количество пассажиров: {order[-2]}\n'
            f'{order[-1]}\n\n'
            f'Дистанция: {order[3]} км.\n'
            f'Оплата: {order[4]} руб.\n'
            f'Дата создания заявки: {order[8]}\n'
            f'Тип оплаты: {"Наличные" if order[9] == "cash" else "С баланса бота"}',
            reply_markup=inline.responde_order(order)
        )


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


async def education(message: Message):

    await message.reply_document(
        document='BQACAgIAAxkBAAIHfmQkZmslL8QnV21XY5qbR7sPFVb_AAJbLQAC2xsgSREfCe7Z9b3jLwQ'
    )


def register_user_handlers(dp: Dispatcher):
    dp.register_message_handler(education, content_types=['document'])
    dp.register_message_handler(star_login, commands=['start'], state='*')
    dp.register_message_handler(profile, lambda msg: msg.text == '👤 Профиль', state="*")
    dp.register_message_handler(order_delivery, lambda mes: mes.text == 'Заказать доставку', state="*")
    dp.register_message_handler(order_taxi, lambda mes: mes.text == '🚕 Заказать такси', state="*")
    dp.register_message_handler(active_orders, lambda mes: mes.text == '🚕 Активные заказы', state="*")
    dp.register_message_handler(support, lambda mes: mes.text == '⚙️ Техническая поддержка', state="*")
    dp.register_message_handler(education, lambda mes: mes.text == '📄 Обучение', state="*")
    dp.register_message_handler(back, lambda mes: mes.text == '⬅️ Вернуться', state='*')

    dp.register_callback_query_handler(change_republics, text='change_region')
    dp.register_message_handler(new_republic, state=ChangeRepublicFSM.republic)

    register_order_tools_handlers(dp)
    register_create_order_handlers(dp)
    register_login_handlers(dp)
    registration_withdrow_handlers(dp)
    register_refill_handlers(dp)
