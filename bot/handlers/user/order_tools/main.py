from datetime import datetime
from asyncio import Lock, get_event_loop

from aiogram import Dispatcher
from aiogram.types import CallbackQuery

from bot.handlers.user.count_down import *
from bot.handlers.utils import *

import bot.Database.methods.get as db_select
import bot.Database.methods.update as db_update

import bot.keyboards.inline as inline
import bot.keyboards.reply as reply

from bot.env import bot

lock = Lock()
loop = get_event_loop()

count_down_list = CountDownList()


async def response(callback: CallbackQuery):

    async with lock:
        await bot.delete_message(
            callback.from_user.id,
            callback.message.message_id
        )

        order_data = callback.data.split(':')

        user_data = await db_select.information_by_user(int(order_data[1]))
        order_data_by_db = await db_select.information_by_order(int(order_data[2]))
        order_user_data = await db_select.information_by_driver(callback.from_user.id)

        #await db_update.change_status_to_order('PROCESSING', order_data[2])
        await db_update.change_driver_id_to_order(order_user_data[1], order_data_by_db[0])

        await bot.send_message(
            int(order_data[1]),
            f'Ваш заказ был принят водителем @{callback.from_user.username}\n\n'
            f'Данные о нем:\n'
            f'Телефон: <b>{order_user_data[5]}</b>\n'
            f'Марка машины: <b>{order_user_data[3]}</b>\n'
            f'Номер машины: <b>{order_user_data[4]}</b>',
            reply_markup=inline.cancel_order(
                user_data[1],
                order_user_data[1],
                order_data_by_db[0]
            ),
            parse_mode='html'
        )
        address_point = await db_select.get_point_loc(order_data[2])

        response_loc = decode_point(address_point)
        loc_latitude, loc_longitude = response_loc.latitude, response_loc.longitude

        route_point_url = yan_maps_point_url.format(loc_latitude, loc_longitude)

        await bot.send_message(
            callback.from_user.id,
            'Данные о заказе:\n\n'
            f'Откуда: {order_data_by_db[1]}\n\n'
            f'Куда: {order_data_by_db[2]}\n\n'
            f'К оплате: {order_data_by_db[4]}\n'
            f'Телефон пассажира: <b>{user_data[3]}</b>\n'
            f'Ссылка: @{user_data[4]}\n\n'
            f'<b>После нажатия на кнопку вы подтвердите что находитесь на месте. <i>Не нажимайте кнопку, если вы еще '
            f'не на месте, в случай ошибки обратитесь в тех. поддержку</i></b>',
            reply_markup=inline.in_place(user_data[1], order_user_data[1], order_data_by_db[0], route_point_url),
            parse_mode='html'
        )


async def in_place(callback: CallbackQuery):

    async with lock:
        await bot.delete_message(
            callback.from_user.id,
            callback.message.message_id
        )

        order_data = callback.data.split(':')

        status = await db_select.get_status_from_order(int(order_data[2]))

        if status[0] == "CANCELED":
            await bot.send_message(
                callback.from_user.id,
                "Данный заказ уже отменен!"
            )

            return

        user_data = await db_select.information_by_user(int(order_data[1]))
        order_data_by_db = await db_select.information_by_order(int(order_data[2]))
        order_user_data = await db_select.information_by_driver(callback.from_user.id)

        new_cd = Countdown(user_data[4], order_data_by_db[0], callback.from_user.id, int(order_data[1]), loop)
        count_down_list.add_count_down(new_cd)

        await db_update.change_status_to_order('INPLACE', order_data[2])

        await bot.send_message(
            int(order_data[1]),
            f'Ваш водитель @{callback.from_user.username} подтвердил что он находится на месте.\n'
            f'Время бесплатного ожидания 5 минут.Дальше цена будет расти как  7 рублей за минуту\n\n'
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
            reply_markup=inline.start_travel(user_data[1], order_user_data[1], order_data_by_db[0]),
            parse_mode='html'
        )


async def start_travel(callback: CallbackQuery):
    async with lock:
        await bot.delete_message(
            callback.from_user.id,
            callback.message.message_id
        )

        order_data = callback.data.split(':')

        status = await db_select.get_status_from_order(int(order_data[2]))

        if status[0] == "CANCELED":
            await bot.send_message(
                callback.from_user.id,
                "Данный заказ уже отменен!"
            )

            return

        user_data = await db_select.information_by_user(int(order_data[1]))
        order_data_by_db = await db_select.information_by_order(int(order_data[2]))
        order_user_data = await db_select.information_by_driver(callback.from_user.id)

        current_cd = count_down_list.get_element_from_count_down_list(order_data_by_db[0])
        count_down_list.remove_count_down(current_cd)
        current_cd_data = current_cd.close_coroutine()

        await db_update.update_total_amount_by_order(
            order_data_by_db[0],
            current_cd_data.get('total_sum')
        )

        await db_update.change_status_to_order('START_TRAVEL', order_data[2])

        await bot.send_message(
            int(order_data[1]),
            f'Ваш водитель @{callback.from_user.username} подтвердил начало поездки.\n\n'
            f'Данные о нем:\n'
            f'Телефон: <b>{order_user_data[5]}</b>\n'
            f'Марка машины: <b>{order_user_data[3]}</b>\n'
            f'Номер машины: <b>{order_user_data[4]}</b>',
            parse_mode='html'
        )

        address = await db_select.get_geocode_location(order_data[2])

        response_loc = decode_location(address)
        location = [(loc.latitude, loc.longitude) for loc in response_loc]

        route_url = yan_maps_navigate_url.format(location[0][0], location[0][1], location[1][0], location[1][1])

        await bot.send_message(
            callback.from_user.id,
            'Данные о заказе:\n\n'
            f'Откуда: {order_data_by_db[1]}\n\n'
            f'Куда: {order_data_by_db[2]}\n\n'
            f'К оплате: {order_data_by_db[4]}\n'
            f'Телефон пассажира: <b>{user_data[3]}</b>\n'
            f'Ссылка: @{user_data[4]}\n\n'
            f'<b>после нажатие на кнопку вы подтвердите что приступили к поездке</b>',
            reply_markup=inline.apply_order(user_data[1], order_user_data[1], order_data_by_db[0], route_url),
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
            f'Заказ №{order_data[1]} успешно подтвержден. С вашего баланса был снята коммисия в размере пяти процентов'
            f'от цена заказа {commision}'
        )

        await bot.send_message(
            order_data[0],
            f'Водитель успешно подтвердил выполнение заказа №{order_data[1]}'
        )


async def cancel_order(callback: CallbackQuery):

    async with lock:
        await bot.delete_message(
            callback.from_user.id,
            callback.message.message_id
        )

    order_data = callback.data.split(':')

    status_order = (await db_select.get_status_from_order(order_data[2]))[0]

    if status_order == 'START_TRAVEL':

        await bot.send_message(
            callback.from_user.id,
            f'Вы не можете отменить заказ т.к. водитель начал его исполнение.',
        )
        return

    if status_order == 'WAITING':
        await db_update.change_status_to_order('CANCELED', order_data[2])

        await bot.send_message(
            callback.from_user.id,
            f'Вы успешно отменили заказ.',
            reply_markup=reply.profile_passenger_markup(),
        )
    else:
        await db_update.remove_balance_from_user(100, callback.from_user.id)
        await db_update.change_status_to_order('CANCELED', order_data[2])

        await bot.send_message(
            callback.from_user.id,
            f'Вы успешно отменили заказ. С вашего счета было списано 100 руб.  \n'
            f'Обращаем внимание что вы не сможете заказывать такси если у вас будет отрицательный баланс в боте\n',
            reply_markup=reply.profile_passenger_markup(),
            parse_mode='html'
        )

        try:
            await bot.send_message(
                int(order_data[3]),
                f'Ваш заказ был отменен пассажиром  @{callback.from_user.username}\n\n'
                f'В случае ошибки обратитесь в тех поддержку',
                reply_markup=reply.profile_driver_markup(),
                parse_mode='html'
            )
        except:
            pass


def register_order_tools_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(cancel_order, inline.cb_cancel.filter(data='cancel_order'))
    dp.register_callback_query_handler(response, inline.cb_data.filter(data='responde'))
    dp.register_callback_query_handler(in_place, inline.cb_arrival.filter(data='in_place'))
    dp.register_callback_query_handler(start_travel, inline.cb_start.filter(data='start_travel'))
    dp.register_callback_query_handler(apply_order, inline.cb_apply.filter(data='apply_order'))