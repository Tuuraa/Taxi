from asyncio import Lock

from aiogram import Dispatcher
from aiogram.types import Message, CallbackQuery
from aiogram.dispatcher import FSMContext
from bot.env import *

from datetime import datetime

from bot.states import CreateRequestWithdrowFSM
import bot.Database.methods.create as db_create
import bot.Database.methods.get as db_select
import bot.keyboards.inline as inline


lock = Lock()


async def profile_driver_btn(callback: CallbackQuery):
    await bot.delete_message(
        callback.from_user.id,
        callback.message.message_id
    )

    await bot.send_message(
        callback.from_user.id,
        "Введите сумму вывода"
    )

    await CreateRequestWithdrowFSM.amount.set()


async def draw_amount(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Это не число")
        return

    if int(message.text) > 100000:
        await message.answer("Слишком большая сумма вывода")
        return

    balance = await db_select.balance_of_driver(message.from_user.id)
    if int(message.text) > balance:
        await message.answer("Не достаточно средств")
        return

    async with state.proxy() as proxy:
        proxy["amount"] = int(message.text)

    await bot.send_message(
       message.from_user.id,
       "Выберите тип банка",
       reply_markup=inline.type_bank_btn()
    )

    await CreateRequestWithdrowFSM.type_bank.set()


async def sber_type(callback: CallbackQuery, state: FSMContext):

    async with state.proxy() as proxy:
        proxy["type_bank"] = "sber"

    await bot.delete_message(
        callback.from_user.id,
        callback.message.message_id
    )

    await bot.send_message(
        callback.from_user.id,
        'Введите номер карты'
    )

    await CreateRequestWithdrowFSM.card.set()


async def sber_card(message: Message, state: FSMContext):
    async with state.proxy() as proxy:

        await db_create.create_withdraw(
            message.from_user.id,
            int(proxy['amount']),
            proxy['type_bank'],
            message.text,
            datetime.now().date()
        )

        await message.answer("Запрос на вывод успешно отправлен, в течении часа ожидайте подтверждения")

    await state.reset_state(with_data=True)


async def tink_type(callback: CallbackQuery, state: FSMContext):
    async with state.proxy() as proxy:
        proxy["type_bank"] = "tink"

    await bot.delete_message(
        callback.from_user.id,
        callback.message.message_id
    )

    await bot.send_message(
        callback.from_user.id,
        'Введите номер карты'
    )

    await CreateRequestWithdrowFSM.card.set()


async def tink_card(message: Message, state: FSMContext):
    async with state.proxy() as proxy:
        date = datetime.now

        await db_create.create_withdraw(
            message.from_user.id,
            int(proxy['amount']),
            date,
            proxy['type_bank'],
            message.text,
        )

        await message.answer("Запрос на вывод успешно отправлен, в течении часа ожидайте подтверждения")

    await state.reset_state(with_data=True)


def registration_withdrow_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(profile_driver_btn, text="withdraw")
    dp.register_message_handler(draw_amount, state=CreateRequestWithdrowFSM.amount)
    dp.register_callback_query_handler(sber_type, state=CreateRequestWithdrowFSM.type_bank, text='sber_type_amount')
    dp.register_callback_query_handler(tink_type, state=CreateRequestWithdrowFSM.type_bank, text='tink_type_amount')
    dp.register_message_handler(sber_card, state=CreateRequestWithdrowFSM.card)
    dp.register_message_handler(tink_card, state=CreateRequestWithdrowFSM.card)

