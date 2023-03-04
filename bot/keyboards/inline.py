from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

import bot.Database.methods.get as db_select


cb_data = CallbackData('ibk', 'user_id', 'id_order', 'data')
cb_apply = CallbackData('ibk', 'user_id', 'driver_id', 'order_id', 'data')
change_pass = CallbackData('ibk', 'user_id', 'data')


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


def apply_order(user_id, order_id, driver_id):
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
    )


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
        InlineKeyboardButton('С багажом', callback_data='with baggage'),
        InlineKeyboardButton('Без багажа', callback_data='without baggage')
    )


def accept_terms_of_use_btns():
    inline = InlineKeyboardMarkup().add(
        InlineKeyboardButton('✅ Принять', callback_data='accept_agreement'),
        InlineKeyboardButton('❌ Отклонить', callback_data='disagree_agreement'),
    )