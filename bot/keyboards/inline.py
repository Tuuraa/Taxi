from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

import bot.Database.methods.get as db_select


cb_data = CallbackData('ibk', 'user_id', 'data')


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


def responde_order():
    return InlineKeyboardMarkup().add(
        InlineKeyboardButton('✌ Отозваться', callback_data='test')
    )
