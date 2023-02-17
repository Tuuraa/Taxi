from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

import bot.Database.methods.get as db_select


def check_status_btns():
    inline = InlineKeyboardMarkup().add(
        InlineKeyboardButton(' Водитель', callback_data='driver'),
        InlineKeyboardButton(' Пассажир', callback_data='passenger'),
    )
    return inline
