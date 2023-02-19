from asyncio import Lock
from aiogram import Dispatcher
from aiogram.types import Message, CallbackQuery, LabeledPrice
from aiogram.dispatcher import FSMContext
from datetime import datetime, timezone

import arrow

from bot.states import TopUpFSM

from bot.env import *

import bot.Database.methods.create as db_create
import bot.Database.methods.get as db_select
import bot.keyboards.inline as inline
import bot.keyboards.reply as reply


lock = Lock()


async def top_up(callback: CallbackQuery):
    await bot.delete_message(
        callback.from_user.id,
        callback.message.message_id
    )

    await bot.send_message(
        callback.from_user.id,
        'Введите сумму для пополнения.'
    )

    await TopUpFSM.amount.set()


async def create_top_up(message: Message, state: FSMContext):
    amount = int(message.text)

    #Здесь пиши оплату АБАЗЭ
    price = LabeledPrice(label="Пополнение", amount=amount * 100)

    if payment_token.split(':')[1] == 'TEST':
        await bot.send_message(message.chat.id, "Тестовый платеж!!!")

    await bot.send_invoice(message.chat.id,
                           title="Пополнение счета",
                           description=f"Пополнение баланса на {amount} руб.",
                           provider_token=payment_token,
                           currency="rub",
                           photo_url="https://www.aroged.com/wp-content/uploads/2022/06/Telegram-has-a-premium-subscription.jpg",
                           photo_width=416,
                           photo_height=234,
                           photo_size=416,
                           is_flexible=False,
                           prices=[price],
                           start_parameter="one-month-subscription",
                           payload="test-invoice-payload")

    await state.reset_state(with_data=True)


def register_refill_handlers(dp:Dispatcher):
    dp.register_callback_query_handler(top_up, text='top_up')
    dp.register_message_handler(create_top_up, state=TopUpFSM.amount)
