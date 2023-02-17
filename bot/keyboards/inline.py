from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

import bot.Database.methods.get as db_select


def checking_the_dr_or_pas_BTNS():
    inline = InlineKeyboardMarkup().add(
        InlineKeyboardButton(' Водитель', callback_data='Driver'),
        InlineKeyboardButton(' Пассажир', callback_data='Passenger'),
    )
    return inline