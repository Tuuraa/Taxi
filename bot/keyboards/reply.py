from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from bot.env import republics


def profile_passenger_markup():
    return ReplyKeyboardMarkup(resize_keyboard=True).add(
        KeyboardButton('👤 Профиль'),
        KeyboardButton('🚕 Заказать такси')
    ).add(
        KeyboardButton('⚙️ Техническая поддержка'),
        #KeyboardButton('Заказать доставку')
    )


def profile_driver_markup():
    return ReplyKeyboardMarkup(resize_keyboard=True).add(
        KeyboardButton('👤 Профиль'),
        KeyboardButton('🚕 Активные заказы')
    ).add(
        KeyboardButton('⚙️ Техническая поддержка')
    )


def set_current_locale():
    return ReplyKeyboardMarkup(resize_keyboard=True).add(
        KeyboardButton('📍 Отправить свою локацию', request_location=True),
        KeyboardButton('⬅️ Вернуться')
    )


def order_location():
    return ReplyKeyboardMarkup(resize_keyboard=True).add(
        KeyboardButton('⬅️ Вернуться')
    )


def all_republics():
    reply = ReplyKeyboardMarkup(resize_keyboard=True)

    for republic in republics:
        reply.add(republic)

    return reply
