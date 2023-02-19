from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

import bot.Database.methods.get as db_select


cb_data = CallbackData('ibk', 'user_id', 'id_order', 'data')


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
        InlineKeyboardButton('💰 Вывести', callback_data='withdraw')
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


def cancel_order():
    return InlineKeyboardMarkup().add(
        InlineKeyboardButton('❌ Отменить заказ', callback_data='test')
    )