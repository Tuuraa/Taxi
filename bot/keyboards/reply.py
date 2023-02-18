from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def profile_markup():
    return ReplyKeyboardMarkup(resize_keyboard=True).add(
        KeyboardButton('👤 Профиль'),
        KeyboardButton('🚕 Заказать такси')
    ).add(
        KeyboardButton('Техническая поддержка')
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