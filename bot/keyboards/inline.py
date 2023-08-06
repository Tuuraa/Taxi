from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData
from aiogram.types.web_app_info import WebAppInfo

import bot.Database.methods.get as db_select


cb_data = CallbackData('ibk', 'user_id', 'id_order', 'data')
cb_apply = CallbackData('ibk', 'user_id', 'driver_id', 'order_id', 'data')
cb_arrival = CallbackData('ibk', 'user_id', 'driver_id', 'order_id', 'data')
cb_start = CallbackData('ibk', 'user_id', 'driver_id', 'order_id', 'data')
cb_cancel = CallbackData('ibk', 'user_id', 'driver_id', 'order_id', 'data')
change_pass = CallbackData('ibk', 'user_id', 'data')
withdraw = CallbackData('ibk', 'id_withdraw', 'data')


def check_status_btns():
    inline = InlineKeyboardMarkup().add(
        InlineKeyboardButton('🚗 Водитель', callback_data='driver'),
        InlineKeyboardButton('👤 Пассажир', callback_data='passenger'),
    )
    return inline


def order_taxi():
    inline = InlineKeyboardMarkup().add(
        InlineKeyboardButton('Заказать', callback_data='order_taxi'),
        InlineKeyboardButton('Отменить', callback_data='cancel_order'),
    )

    return inline


def profile_passenger_btn():
    return InlineKeyboardMarkup().add(
        InlineKeyboardButton('💸 Пополнить', callback_data='top_up')
    )


def profile_driver_btn():
    return InlineKeyboardMarkup().add(
        InlineKeyboardButton('💰 Вывести', callback_data='withdraw'),
        InlineKeyboardButton("Сменить республику", callback_data="change_region")
    )


def type_bank_btn():
    inline = InlineKeyboardMarkup().add(
        InlineKeyboardButton("Сбербанк", callback_data="sber_type_amount"),
        InlineKeyboardButton("Тинькофф", callback_data="tink_type_amount")
    )

    return inline


def responde_order(order):
    return InlineKeyboardMarkup().add(
        InlineKeyboardButton(
            '✌ Отозваться',
            callback_data=cb_data.new(
                user_id=order[5],
                id_order=order[0],
                data='responde'
            )
        )
    )


def apply_order(user_id, order_id, driver_id, route_url):
    return InlineKeyboardMarkup().add(
        InlineKeyboardButton(
            'Подтвердить выполнение заказа',
            callback_data=cb_apply.new(
                user_id=user_id,
                order_id=order_id,
                driver_id=driver_id,
                data='apply_order'
            )
        )
    ).add(
        InlineKeyboardButton(
            "Построить маршрут",
            web_app=WebAppInfo(url=route_url)
        ))


def change_user(user_id):
    return InlineKeyboardMarkup().add(
        InlineKeyboardButton(
            'Изменить',
            callback_data=change_pass.new(
                user_id=user_id,
                data='change_user'
            )
        )
    )


def pay_order():
    return InlineKeyboardMarkup().add(
        InlineKeyboardButton('Заплатить наличными', callback_data='pay_by_cash')
    ).add(
        InlineKeyboardButton('Снять с баланса бота', callback_data='pay_by_wallet')
    )


def pay_delivery():
    return InlineKeyboardMarkup().add(
        InlineKeyboardButton('Заплатить наличными', callback_data='del_pay_by_cash')
    ).add(
        InlineKeyboardButton('Снять с баланса', callback_data='del_pay_by_wallet')
    )


def not_enough_amount():
    return InlineKeyboardMarkup().add(
        InlineKeyboardButton('Заплатить наличными', callback_data='pay_by_cash'),
        InlineKeyboardButton('💸 Пополнить', callback_data='top_up')
    )


def baggage_availability():
    return InlineKeyboardMarkup().add(
        InlineKeyboardButton('С багажом', callback_data='with_baggage'),
        InlineKeyboardButton('Без багажа', callback_data='without_baggage')
    )


def accept_terms_of_use_btns():
    return InlineKeyboardMarkup().add(
        InlineKeyboardButton('✅ Принять', callback_data='accept_agreement'),
        InlineKeyboardButton('❌ Отклонить', callback_data='disagree_agreement'),
    )


def send_info_to_mail():
    return InlineKeyboardMarkup().add(
        InlineKeyboardButton('✅ Отправил', callback_data='send_info')
    )


def withdraw_items(id_withdraw):
    return InlineKeyboardMarkup().add(
        InlineKeyboardButton(
            'Изменить статус',
            callback_data=withdraw.new(
                id_withdraw=id_withdraw,
                data='change_withdraw',
            )
        )
    )


def in_place(user_id, order_id, driver_id):
    return InlineKeyboardMarkup().add(
        InlineKeyboardButton(
            'Подтвердить что вы на месте',
            callback_data=cb_arrival.new(
                user_id=user_id,
                order_id=order_id,
                driver_id=driver_id,
                data='in_place'
            )
        )
    )


def start_travel(user_id, order_id, driver_id):
    return InlineKeyboardMarkup().add(
        InlineKeyboardButton(
            'Подтвердить начало поедзки',
            callback_data=cb_start.new(
                user_id=user_id,
                order_id=order_id,
                driver_id=driver_id,
                data='start_travel'
            )
        )
    )


def cancel_order(user_id, order_id, driver_id):
    return InlineKeyboardMarkup().add(
        InlineKeyboardButton(
            'Отменить заказ',
            callback_data=cb_cancel.new(
                user_id=user_id,
                order_id=order_id,
                driver_id=driver_id,
                data='cancel_order'
            )
        )
    )
