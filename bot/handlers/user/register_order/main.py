from datetime import datetime
from asyncio import Lock

from aiogram.types import CallbackQuery, Message
from aiogram.dispatcher import FSMContext
from aiogram import Dispatcher

import bot.Database.methods.create as db_create
import bot.Database.methods.get as db_select

from bot.handlers.utils import *

import bot.keyboards.inline as inline
import bot.keyboards.reply as reply

from bot.env import *
from bot.states import *


lock = Lock()


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
                f'Расстояние составляет: {round(distance * 1.56)} км.\n'
                f'Время пути составит: {round(distance / 50)} ч.\n'
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
            f'Расстояние составляет: {round(distance * 1,56)} км.\n'
            f'Время пути составит: {round(distance / 50)} ч.\n'
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

        distance = int(proxy['distance'])
        amount = int(proxy['amount'])

        await bot.send_message(
            callback.from_user.id,
            'Заказ успешно создан.\n'
            f'Расстояние составляет: {round(distance * 1, 56)} км.\n'
            f'Время пути составит: {distance / 50} ч.\n'
            f'Сумма к оплате: {amount} руб.\n',
            reply_markup=reply.profile_passenger_markup()
        )

        await bot.send_message(
            callback.from_user.id,
            'Вы также можете его отменить  в случае ошибки.',
            reply_markup=inline.cancel_order(
                callback.from_user.id,
                0,
                await db_select.get_last_id_from_orders()
            )
        )

        await send_order_to_all_drivers(proxy['republic'], proxy['amount'])

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

            distance = int(proxy['distance'])
            amount = int(proxy['amount'])

            await bot.send_message(
                callback.from_user.id,
                'Заказ успешно создан.\n'
                f'Расстояние составляет: {round(distance * 1,56)} км.\n'
                f'Время пути составит: {distance / 50} ч.\n'
                f'Сумма к оплате: {amount} руб.\n',
                reply_markup=reply.profile_passenger_markup()
            )

            await bot.send_message(
                callback.from_user.id,
                'Вы также можете его отменить  в случае ошибки.',
                reply_markup=inline.cancel_order(
                    callback.from_user.id,
                    0,
                    await db_select.get_last_id_from_orders()
                )
            )

            await send_order_to_all_drivers(proxy['republic'], proxy['amount'])

            await state.reset_state(with_data=True)


def register_create_order_handlers(dp: Dispatcher):
    dp.register_message_handler(current_user_location_handler, state=UserLocationFSM.current_location,
                                content_types=['location', 'text'])
    dp.register_message_handler(current_delivery_location, state=DeliveryFSM.current_delivery_location,
                                content_types=['location', 'text'])
    dp.register_message_handler(delivery_order_location, state=DeliveryFSM.delivery_order_location,
                                content_types=['location', 'text'])
    dp.register_message_handler(order_location, state=UserLocationFSM.order_location,
                                content_types=['location', 'text'])

    dp.register_callback_query_handler(pay_by_cash, text='pay_by_cash', state=UserLocationFSM.type_pay)
    dp.register_callback_query_handler(pay_by_wallet, text='pay_by_wallet', state=UserLocationFSM.type_pay)

    dp.register_message_handler(number_of_passengers, state=UserLocationFSM.numbers_of_users)
    dp.register_callback_query_handler(with_baggage, state=UserLocationFSM.is_baggage, text='with_baggage')
    dp.register_callback_query_handler(without_baggage, state=UserLocationFSM.is_baggage, text='without_baggage')
