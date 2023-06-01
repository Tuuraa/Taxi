from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from bot.env import republics


def profile_passenger_markup():
    return ReplyKeyboardMarkup(resize_keyboard=True).add(
        KeyboardButton('👤 Профиль'),
        KeyboardButton('🚕 Заказать такси')
    ).add(
        KeyboardButton('⚙️ Техническая поддержка'),
        KeyboardButton('📄 Обучение')
    )


def profile_driver_markup():
    return ReplyKeyboardMarkup(resize_keyboard=True).add(
        KeyboardButton('👤 Профиль'),
        KeyboardButton('🚕 Активные заказы')
    ).add(
        KeyboardButton('⚙️ Техническая поддержка'),
        KeyboardButton('📄 Обучение')
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


def admin_panel_btns():
    return ReplyKeyboardMarkup(resize_keyboard=True).add(
        'Искать пользователя', 'Искать водителя'
    ).add(
        'Заказы', 'Выводы', 'Переключить на пассажира'
    )


def orders_btns():
    return ReplyKeyboardMarkup(resize_keyboard=True).add(
        'По республике', 'По id'
    )


def status_orders():
    return ReplyKeyboardMarkup(resize_keyboard=True).add(
        'В ожидании', 'Выполнено', 'В процессе'
    )


def status_withdraws():
    return ReplyKeyboardMarkup(resize_keyboard=True).add(
        'Выполнено', 'Отменено'
    )



def change_user_list():
    return ReplyKeyboardMarkup(resize_keyboard=True).add(
        'ФИО', 'Телефон', 'Баланс'
    )


def change_driver_list():
    return ReplyKeyboardMarkup(resize_keyboard=True).add(
        'ФИО', 'Телефон', 'Баланс', 'Марка машины', 'Номер машины',
        'Республика'
    )

