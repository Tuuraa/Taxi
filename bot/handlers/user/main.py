from asyncio import Lock
from datetime import datetime

from aiogram import Dispatcher
from aiogram.types import Message, CallbackQuery
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


async def number_of_passengers(message: Message, state: FSMContext):

    if not message.text.isdigit():
        await message.answer("Вы ввели не число!")
        return

    if int(message.text) > 30:
        await message.answer(
            "Слишком большое количество пассажиров"
        )
        return

    async with state.proxy() as proxy:
        proxy['numbers_of_users'] = int(message.text)

    await message.answer(
        'Поездка осуществляется:',
        reply_markup=inline.baggage_availability()
    )

    await UserLocationFSM.is_baggage.set()


async def with_baggage(callback: CallbackQuery, state: FSMContext):

    await bot.delete_message(
        callback.from_user.id,
        callback.message.message_id
    )

    async with state.proxy() as proxy:
        proxy['is_baggage'] = 'С багажом'

    await bot.send_message(
        callback.from_user.id,
        'Отправьте локацию, либо введите адресс вручную по примеру\n'
        'Черкесск, Кавказская 73',
        reply_markup=reply.set_current_locale()
    )

    await UserLocationFSM.current_location.set()


async def without_baggage(callback: CallbackQuery, state: FSMContext):

    await bot.delete_message(
        callback.from_user.id,
        callback.message.message_id
    )

    async with state.proxy() as proxy:
        proxy['is_baggage'] = 'Без багажа'

    await bot.send_message(
        callback.from_user.id,
        'Отправьте локацию, либо введите адрес вручную по примеру\n'
        'Черкесск, Кавказская 73',
        reply_markup=reply.set_current_locale()
    )

    await UserLocationFSM.current_location.set()


async def current_user_location_handler(message: Message, state: FSMContext):
    location = current_user_location(message)

    if location:

        async with state.proxy() as proxy:
            proxy['current_location'] = location[0], location[1], location[2]

        await message.answer(
            "А теперь куда хотите заказать такси.\n"
            "Для этого нажмите на скрепку 📎, и оправьте локацию, или адрес вручную куда хотите поехать\n\n"
            "<b><i>Обратите внимание, адрес должен быть точно указан.</i></b>",
            parse_mode='html',
            reply_markup=reply.order_location()
        )

        await UserLocationFSM.next()
    else:
        await message.answer(
            'Не удалось распознать адрес, введите более конкретный'
        )


async def order_location(message: Message, state: FSMContext):
    location = current_user_location(message)

    if location:
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
                    reply_markup=reply.profile_passenger_markup() if user_data == 'passenger'
                        else reply.profile_driver_markup()
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

            if distance < 2:
                amount = 75
            elif 50 >= distance > 2:
                distance = int(distance)
                coef = ways[distance]
                if distance < 4:
                    amount = 75 + coef * (distance - 1) + 5 * (3 + ((distance / 50) * 60) - 5)
                else:
                    amount = 75 + coef * (distance - 1) + 5 * (1 + ((distance / 50) * 60) - 5)
            else:
                distance = int(distance)
                coef = ways[len(ways)]
                amount = 75 + coef * (distance - 1) + 5 * (1 + distance / 50 - 5)
                other_sum = int((distance - len(ways)) / 3) * 82
                amount += other_sum

            amount = round(amount, 2)

            proxy['distance'] = distance
            proxy['time'] = distance / 50
            proxy['amount'] = amount
            proxy['republic'] = republic

            await message.answer(
                f'Расстояние состовляет: {distance} км.\n'
                f'Время пути составит: {distance / 50} ч.\n'
                f'Сумма к оплате: {amount} руб.\n'
                f'Выберите каким образом будете оплачивать',
                reply_markup=inline.pay_order()
            )

            await UserLocationFSM.type_pay.set()
    else:
        await message.answer(
            'Не удалось распознать адрес, введите более конкретный'
        )


async def current_delivery_location(message: Message, state: FSMContext):
    location = current_user_location(message)

    async with state.proxy() as proxy:
        proxy['current_delivery_location'] = location[0], location[1], location[2]

    await message.answer(
        "А теперь куда хотите заказать доставку.\n"
        "Для этого нажмите на скрепку 📎, и оправьте локацию, куда хотите поехать\n\n"
        "<b><i>Обратите внимание, адрес должен быть точно указан.</i></b>",
        reply_markup=reply.order_location()
    )

    await DeliveryFSM.next()


async def delivery_order_location(message: Message, state: FSMContext):
    location = current_user_location(message)

    async with state.proxy() as proxy:
        proxy['delivery_order_location'] = location[0], location[1], location[2]

        location_list = proxy['current_delivery_location'][0].address.split(', ')
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
            f'Откуда:\n{proxy["current_delivery_location"][0]}'
        )

        await message.answer(
            f'Куда:\n{location[0]}'
        )

        first_loc = proxy['current_delivery_location'][1], proxy['current_delivery_location'][2]
        second_loc = proxy['delivery_order_location'][1], proxy['delivery_order_location'][2]

        distance = round(distance_btw_two_points(
            current_point=first_loc,
            order_point=second_loc
        ).km, 3)

        amount = 75 + 10 * (distance - 1) + 5 * (1 + distance / 50 - 5)

        proxy['delivery_distance'] = distance
        proxy['delivery_time'] = round(distance / 50, 2)
        proxy['delivery_amount'] = amount
        proxy['republic'] = republic

        await message.answer(
            f'Расстояние состовляет: {distance} км.\n'
            f'Время пути составит: {distance / 50} ч.\n'
            f'Сумма к оплате: {amount} руб.\n'
            f'Выберите каким образом будете оплачивать',
            reply_markup=inline.pay_delivery()
        )

        await DeliveryFSM.delivery_type_pay.set()


async def pay_by_cash(callback: CallbackQuery, state: FSMContext):

    await bot.delete_message(
        callback.from_user.id,
        callback.message.message_id
    )

    async with state.proxy() as proxy:
        proxy['type_pay'] = 'cash'

        await db_create.create_order(
             callback.from_user.id,
             proxy["current_location"][0],
             proxy["order_location"][0],
             proxy['distance'],
             proxy['amount'],
             proxy['republic'],
             datetime.now(),
             'cash',
             proxy['time'],
             proxy['numbers_of_users'],
             proxy['is_baggage']
         )

        await bot.send_message(
            callback.from_user.id,
            'Заказ успешно создан.',
            reply_markup=reply.profile_passenger_markup()
        )

        await send_order_to_all_drivers(proxy['republic'], proxy['amount'])

        await state.reset_state(with_data=True)


async def del_pay_by_cash(callback: CallbackQuery, state: FSMContext):

    await bot.delete_message(
        callback.from_user.id,
        callback.message.message_id
    )

    async with state.proxy() as proxy:
        proxy['delivery_type_pay'] = 'cash'

        await db_create.create_delivery(
            callback.from_user.id,
            proxy['current_delivery_location'][0],
            proxy['delivery_order_location'][0],
            proxy['delivery_distance'],
            proxy['delivery_amount'],
            proxy['republic'],
            datetime.now(),
            'cash'
        )

        await bot.send_message(
            callback.from_user.id,
            'Заказ успешно создан',
            reply_markup=reply.profile_passenger_markup()
        )
        await state.reset_state(with_data=True)


async def del_pay_by_wallet(callback: CallbackQuery, state: FSMContext):
    await bot.delete_message(
        callback.from_user.id,
        callback.message.message_id
    )

    async with lock:
        async with state.proxy() as proxy:
            user_balance = await db_select.balance_by_user(callback.from_user.id)

            if user_balance < int(proxy['delivery_amount']):
                await bot.send_message(
                    callback.from_user.id,
                    'Недостаточно средств для заказа такси. Необходимо пополнить баланс, либо выбрать другой тип оплаты',
                    reply_markup=inline.not_enough_amount()
                )
                return

            await db_create.create_delivery(
                proxy["current_location"][0],
                proxy["order_location"][0],
                proxy['distance'],
                proxy['amount'],
                proxy['republic'],
                datetime.now(),
                'wallet',
                proxy['time'],

            )

            await bot.send_message(
                callback.from_user.id,
                'Заказ успешно создан.',
                reply_markup=reply.profile_passenger_markup()
            )

            await state.reset_state(with_data=True)


async def pay_by_wallet(callback: CallbackQuery, state: FSMContext):

    await bot.delete_message(
        callback.from_user.id,
        callback.message.message_id
    )

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
                'wallet',
                proxy['time'],
                proxy['numbers_of_users'],
                proxy['is_baggage']
            )

            await bot.send_message(
                callback.from_user.id,
                'Заказ успешно создан.',
                reply_markup=reply.profile_passenger_markup()
            )

            await send_order_to_all_drivers(proxy['republic'], proxy['amount'])

            await state.reset_state(with_data=True)


async def order_delivery(message: Message, state: FSMContext):

    await state.reset_state(with_data=True)

    await message.answer(
        'Отправьте локацию, либо пропишите ее вручную',
        reply_markup=reply.set_current_locale()
    )

    await DeliveryFSM.current_delivery_location.set()


async def order_taxi(message: Message, state: FSMContext):

    if not await db_select.check_user_from_order(message.from_user.id):
        await message.answer("У вас уже есть активные заказы")
        return

    await state.reset_state(with_data=True)

    await message.answer(
        "Какое количество пассажиров поедет.\n"
        "Обратите внимание количество пассажиров должно быть точно указано"
    )

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


async def responde(callback: CallbackQuery):
    async with lock:
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
            f'Ссылка: @{user_data[4]}\n\n'
            f'<b>После нажатия на кнопку деньги будут списаны с счета заказчика. <i>Не нажимайте кнопку, если вы еще '
            f'не выполнили заказ, в случай ошибки обратитесь в тех. поддержку</i></b>',
            reply_markup=inline.apply_order(user_data[1], order_user_data[1], order_data_by_db[0]),
            parse_mode='html'
        )


async def apply_order(callback: CallbackQuery):

    await bot.delete_message(
        callback.from_user.id,
        callback.message.message_id
    )

    order_data = [int(item) for item in callback.data.split(':')[1:-1]]
    await db_update.change_status_to_order('COMPLETED', order_data[1])
    await db_update.change_complete_order(datetime.now(), order_data[1])
    order = await db_select.information_by_order(order_data[1])
    accrual_amount = order[4] - ((order[4] / 100) * 5)
    commision = (order[4] / 100) * 5

    if order[9] == 'wallet':
        await db_update.add_balance_from_driver(accrual_amount, order_data[2])
        await db_update.remove_balance_from_user(order[4], order_data[0])

        await bot.send_message(
            callback.from_user.id,
            f'Вы успешно подтвердили выполнение заказа №{order_data[1]}. Ваш баланс пополнен на {accrual_amount} р.'
        )

        await bot.send_message(
            order_data[0],
            f'Заказ №{order_data[1]} был подтвержден водителем. С вашего баланса было снято {order[4]} р.\n'
            f'В случай ошибки напишите в тех. поддержку.'
        )
    else:
        await db_update.remove_balance_from_driver(commision, order_data[2])

        await bot.send_message(
            callback.from_user.id,
            f'Заказ №{order_data[1]} успешно подтвержден.С вашего баланса был снята коммисия в размере пяти процентов'
            f'от цена заказа {commision}'
        )

        await bot.send_message(
            order_data[0],
            f'Водитель успешно подтвердил выполнение заказа №{order_data[1]}'
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
    dp.register_message_handler(current_user_location_handler, state=UserLocationFSM.current_location,
                                content_types=['location', 'text'])
    dp.register_message_handler(current_delivery_location, state=DeliveryFSM.current_delivery_location,
                                content_types=['location', 'text'])
    dp.register_message_handler(delivery_order_location, state=DeliveryFSM.delivery_order_location,
                                content_types=['location', 'text'])
    dp.register_message_handler(order_location, state=UserLocationFSM.order_location,
                                content_types=['location', 'text'])

    dp.register_callback_query_handler(del_pay_by_cash, text='del_pay_by_cash',
                                       state=DeliveryFSM.delivery_type_pay)
    dp.register_callback_query_handler(del_pay_by_wallet, text='del_pay_by_wallet',
                                       state=DeliveryFSM.delivery_type_pay)
    dp.register_callback_query_handler(pay_by_cash, text='pay_by_cash', state=UserLocationFSM.type_pay)
    dp.register_callback_query_handler(pay_by_wallet, text='pay_by_wallet', state=UserLocationFSM.type_pay)

    dp.register_callback_query_handler(responde, inline.cb_data.filter(data='responde'))
    dp.register_callback_query_handler(apply_order, inline.cb_apply.filter(data='apply_order'))

    dp.register_message_handler(number_of_passengers, state=UserLocationFSM.numbers_of_users)
    dp.register_callback_query_handler(with_baggage, state=UserLocationFSM.is_baggage, text='with_baggage')
    dp.register_callback_query_handler(without_baggage, state=UserLocationFSM.is_baggage, text='without_baggage')

    register_login_handlers(dp)
    registration_withdrow_handlers(dp)
    register_refill_handlers(dp)
