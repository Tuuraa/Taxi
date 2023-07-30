from asyncio import Lock
from aiogram import Dispatcher
from aiogram.types import Message, CallbackQuery, LabeledPrice, ContentType, PreCheckoutQuery
from aiogram.dispatcher import FSMContext
from datetime import datetime, timezone
from aiogram.types.message import ContentType

from bot.states import TopUpFSM

from bot.env import *

import bot.Database.methods.create as db_create
import bot.Database.methods.update as db_update

lock = Lock()


async def top_up(callback: CallbackQuery, state: FSMContext):

    await state.reset_state(with_data=True)

    await bot.delete_message(
        callback.from_user.id,
        callback.message.message_id
    )

    await bot.send_message(
        callback.from_user.id,
        'Введите сумму для пополнения. От 15 руб.'
    )

    await TopUpFSM.amount.set()


async def create_top_up(message: Message, state: FSMContext):
    amount = int(message.text)

    price = LabeledPrice(label="Пополнение", amount=amount * 100)

    await bot.send_invoice(
        message.chat.id,
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
        payload="payload",
    )

    await state.reset_state(with_data=True)


async def pre_checkout_query(pre_checkout_q: PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_q.id, ok=True)


async def successful_payment(message: Message):
    async with lock:
        total_amount = message.successful_payment.total_amount / 100
        await bot.send_message(message.chat.id,
            f"Платеж на сумму "
            f"{total_amount} "
            f"{message.successful_payment.currency} прошел успешно!!!"
        )

        await db_update.add_top_up(
            message.from_user.id,
            total_amount
        )
        await db_create.create_refill(
            message.from_user.id,
            total_amount,
            datetime.now()
        )


def register_refill_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(top_up, text='top_up', state='*')
    dp.register_message_handler(create_top_up, state=TopUpFSM.amount)
    dp.register_pre_checkout_query_handler(pre_checkout_query, lambda query: True)
    dp.register_message_handler(successful_payment, content_types=ContentType.SUCCESSFUL_PAYMENT)
    dp.register_message_handler(successful_payment, content_types=ContentType.SUCCESSFUL_PAYMENT)