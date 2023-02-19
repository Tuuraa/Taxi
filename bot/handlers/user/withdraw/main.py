from asyncio import Lock

import callback as callback
from aiogram import Dispatcher
from aiogram.types import Message, CallbackQuery
from aiogram.dispatcher import FSMContext
from bot.env import *


from bot.states import CreateRequestWithdrowFSM
import bot.Database.methods.create as db_create
import bot.Database.methods.get as db_select
import bot.keyboards.inline as inline


lock = Lock()


def profile_driver_btn(callback: CallbackQuery):
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

    await bot.send_message(
       message.from_user.id,
       "Выберите тип банка",
       reply_markup=inline.type_bank_btn
    )

    await CreateRequestWithdrowFSM.type_bank.set()


async def sber_type(callback: CallbackQuery, state: FSMContext):
    await bot.delete_message(
        callback.from_user.id,
        callback.message.message_id
    )

    async with state.proxy() as proxy:
        proxy["type_bank"] = "sber"


   await bot.send_message(
       callback.from_user.id

   )





def registration_withdrow_btns(dp: Dispatcher):
    dp.register_callback_query_handler(profile_driver_btn, text="withdraw_btn")
    dp.register_callback_query_handler(sber_type,)