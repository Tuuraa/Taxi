from asyncio import Lock
from aiogram import Dispatcher
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.dispatcher import FSMContext

import bot.Database.methods.get as db_select
import bot.Database.methods.update as db_update

import bot.keyboards.inline as inline
import bot.keyboards.reply as reply

from bot.env import *
from bot.handlers.utils import *
from bot.states import *

lock = Lock()


async def search_user(message: Message, state: FSMContext):
    await state.reset_state(with_data=True)

    await message.answer(
        'Введите id пользователя: '
    )

    await SearchPassengerFSM.name.set()


async def data_of_passenger(message: Message, state: FSMContext):
    user_data = await db_select.information_by_user(message.text)

    if user_data:
        await message.answer(
            f'🤖 ID: <b>{user_data[1]}</b>\n'
            f'👤 ФИО: <b>{user_data[2]}\n</b>'
            f'📱 Телефон: <b>{user_data[3]}</b>\n'
            f'💰 Баланс: <b>{user_data[-1]}</b> руб',
            parse_mode='html',
            reply_markup=inline.change_user(message.text)
        )
    else:
        await message.answer(
            'Нет такого пассажира'
        )

    await state.reset_state(with_data=True)
    await ChangeDataUserFSM.user_id.set()


async def change_user(callback: CallbackQuery, state: FSMContext):

    async with state.proxy() as proxy:
        proxy['user_id'] = int(callback.data.split(':')[1])

    await bot.delete_message(
        callback.from_user.id,
        callback.message.message_id
    )

    await bot.send_message(
        callback.from_user.id,
        'Выберите поле, которое хотите изменить \n',
        reply_markup=reply.change_user_list()
    )

    await ChangeDataUserFSM.next()


async def changed_user(message: Message, state: FSMContext):

    async with state.proxy() as proxy:
        proxy['changed'] = message.text

    await message.answer(
        'А теперь на какое значение хотите изменить',
        reply_markup=ReplyKeyboardRemove()
    )

    await ChangeDataUserFSM.next()


async def update_user_data(message: Message, state: FSMContext):
    async with state.proxy() as proxy:

        if proxy['changed'] == 'ФИО':
            await db_update.update_name_from_user(message.text, int(proxy['user_id']))
        elif proxy['changed'] == 'Телефон':
            await db_update.update_phone_from_user(message.text, int(proxy['user_id']))
        else:
            await db_update.update_balance_from_user(message.text, int(proxy['user_id']))

        await message.answer(
            'Данные успешно обновлены',
            reply_markup=reply.admin_panel_btns()
        )

    await state.reset_state(with_data=True)

#----------------------------------------------------------------


async def search_driver(message: Message, state: FSMContext):
    await state.reset_state(with_data=True)

    await message.answer(
        'Введите id водителя: '
    )

    await SearchDriverFSM.name.set()


async def data_of_driver(message: Message, state: FSMContext):

    driver_data = await db_select.information_by_driver(message.text)

    if driver_data:
        await message.answer(
            f'🤖 ID: <b>{driver_data[1]}</b>\n'
            f'👤 ФИО: <b>{driver_data[2]}</b>\n'
            f'📱 Телефон: <b>{driver_data[5]}</b>\n\n'
            f'🚗 Марка машины: <b>{driver_data[3]}</b>\n'
            f'🚕 Номер машины: <b>{driver_data[4]}</b>\n'
            f'⛰ Республика: <b>{driver_data[8]}</b>\n'
            f'💵 Баланс: <b>{driver_data[9]}</b> руб\n',
            parse_mode='html',
            reply_markup=inline.change_user(message.text)
        )
    else:
        await message.answer(
            'Нет такого водителя'
        )

    await state.reset_state(with_data=True)
    await ChangeDataDriverFSM.user_id.set()


async def change_driver(callback: CallbackQuery, state: FSMContext):
    async with state.proxy() as proxy:
        proxy['user_id'] = int(callback.data.split(':')[1])

    await bot.delete_message(
        callback.from_user.id,
        callback.message.message_id
    )

    await bot.send_message(
        callback.from_user.id,
        'Выберите поле, которое хотите изменить \n',
        reply_markup=reply.change_driver_list()
    )

    await ChangeDataDriverFSM.next()


async def changed_driver(message: Message, state: FSMContext):
    async with state.proxy() as proxy:
        proxy['changed'] = message.text

    if message.text == 'Республика':
        await message.answer(
            'А теперь на какое значение хотите изменить',
            reply_markup=reply.all_republics()
        )
    else:
        await message.answer(
            'А теперь на какое значение хотите изменить',
            reply_markup=ReplyKeyboardRemove()
        )

    await ChangeDataDriverFSM.next()


async def update_driver_data(message: Message, state: FSMContext):
    async with state.proxy() as proxy:

        if proxy['changed'] == 'ФИО':
            await db_update.update_name_from_driver(message.text, int(proxy['user_id']))
        elif proxy['changed'] == 'Телефон':
            await db_update.update_phone_from_driver(message.text, int(proxy['user_id']))
        elif proxy['changed'] == 'Баланс':
            await db_update.update_balance_from_driver(message.text, int(proxy['user_id']))
        elif proxy['changed'] == 'Марка машины':
            await db_update.update_mark_from_driver(message.text, int(proxy['user_id']))
        elif proxy['changed'] == 'Номер машины':
            await db_update.update_car_number_from_driver(message.text, int(proxy['user_id']))
        else:
            await db_update.update_republic_from_driver(message.text, int(proxy['user_id']))

        await message.answer(
            'Данные успешно обновлены',
            reply_markup=reply.admin_panel_btns()
        )

    await state.reset_state(with_data=True)


#-----------------------------------------------------------------------

async def orders(message: Message, state: FSMContext):
    await state.reset_state(with_data=True)

    await message.answer(
        'Выберите каким образом будете искать заказ',
        reply_markup=reply.orders_btns()
    )


async def orders_by_republic(message: Message):
    await message.answer(
        'Выберите республику',
        reply_markup=reply.all_republics()
    )

    await OrdersByRepublicFSM.republic.set()


async def status_order(message: Message, state: FSMContext):

    async with state.proxy() as proxy:
        proxy['republic'] = message.text

    await message.answer(
        'Выберите статус',
        reply_markup=reply.status_orders()
    )

    await OrdersByRepublicFSM.next()


async def orders_by_data(message: Message, state: FSMContext):
    async with state.proxy() as proxy:
        orders = await db_select.orders_by_status_and_republic(proxy['republic'], orders_data[message.text])

        if orders:
            for order in orders:
                await message.answer(
                    f'Заказ №{order[0]}\n\n'
                    f'Откуда: {order[1]}\n\n'
                    f'Куда: {order[2]}\n\n'
                    f'Дистанция: {order[3]} км.\n'
                    f'Время: {order[-4]} ч.\n'
                    f'Оплата: {order[4]} руб.\n'
                    f'Дата создания заявки: {order[8]}\n'
                    f'Дата выполнения заказа: {order[-3]}\n'
                    f'Тип оплаты: {"Наличные" if order[9] == "cash" else "С баланса бота"}',
                    reply_markup=reply.admin_panel_btns()
                )
        else:
            await message.answer(
                'Нет таких заказов',
                reply_markup=reply.admin_panel_btns()
            )
    await state.reset_state(with_data=True)


async def order_by_id(message: Message):
    await message.answer(
        'Введите id заказа:',
        reply_markup=ReplyKeyboardRemove()
    )

    await OrderByIdFSM.id.set()


async def order_by_id_answer(message: Message, state: FSMContext):

    if not message.text.isdigit():
        await message.answer('Это не число')

    order = await db_select.information_by_order(int(message.text))

    if order:
        await message.answer(
            f'Заказ №{order[0]}\n\n'
            f'Откуда: {order[1]}\n\n'
            f'Куда: {order[2]}\n\n'
            f'Статус: {get_key(order[6])}\n\n'
            f'Дистанция: {order[3]} км.\n'
            f'Время: {order[-2]} ч.\n'
            f'Оплата: {order[4]} руб.\n'
            f'Дата создания заявки: {order[8]}\n'
            f'Дата выполнения заказа: {order[-1]}\n'
            f'Тип оплаты: {"Наличные" if order[9] == "cash" else "С баланса бота"}',
            reply_markup=reply.admin_panel_btns()
        )
    else:
        await message.answer(
            'Нет такого заказа',
            reply_markup=reply.admin_panel_btns()
        )

    await state.reset_state(with_data=True)


async def swap(message: Message):
    await message.answer(
        'Переключено на пассажира, чтобы вернуться обратно нажмите на /start',
        reply_markup=reply.profile_passenger_markup()
    )


async def send_all_withdraw(message: Message):
    withdraws = await db_select.all_withdraws()

    for withdraw in withdraws:
        await message.answer(
            f'Id: {withdraw[0]} \n\n'
            f'Id юзера: {withdraw[1]} \n'
            f'Сумма: {withdraw[2]} руб. \n'
            f'Банк: {"Сбербанк" if withdraw[3] == "sber" else "Тинькофф"} \n'
            f'Номер карты: {withdraw[4]}',
            reply_markup=inline.withdraw_items(withdraw[0])
        )

    await WithdrawFSM.id_withdraw.set()


async def change_status_to_withdraw(callback: CallbackQuery, state: FSMContext):

    await bot.delete_message(
        callback.from_user.id,
        callback.message.message_id
    )

    async with state.proxy() as proxy:
        proxy['id_withdraw'] = callback.data.split(":")[1]

    await bot.send_message(
        callback.from_user.id,
        'Выберите статус',
        reply_markup=reply.status_withdraws()
    )

    await WithdrawFSM.status.set()


async def update_status_to_withdraw(message: Message, state: FSMContext):

    async with state.proxy() as proxy:
        await db_update.update_status_from_withdraw(message.text ,proxy.get('id_withdraw'))

    await message.answer(
        'Готово',
        reply_markup=reply.admin_panel_btns()
    )

    await state.reset_state(with_data=True)


def register_admin_handlers(dp: Dispatcher):
    dp.register_message_handler(search_user, lambda mes: mes.text == 'Искать пользователя', state='*')
    dp.register_message_handler(search_driver, lambda mes: mes.text == 'Искать водителя', state='*')
    dp.register_message_handler(orders, lambda mes: mes.text == 'Заказы', state='*')
    dp.register_message_handler(send_all_withdraw, lambda mes: mes.text == 'Выводы', state='*')
    dp.register_message_handler(swap, lambda mes: mes.text == 'Переключить на пассажира', state='*')

    dp.register_message_handler(data_of_passenger, state=SearchPassengerFSM.name)
    dp.register_callback_query_handler(change_user, state=ChangeDataUserFSM.user_id)
    dp.register_message_handler(changed_user, state=ChangeDataUserFSM.changed)
    dp.register_message_handler(update_user_data, state=ChangeDataUserFSM.data)

    dp.register_message_handler(data_of_driver, state=SearchDriverFSM.name)
    dp.register_callback_query_handler(change_driver, state=ChangeDataDriverFSM.user_id)
    dp.register_message_handler(changed_driver, state=ChangeDataDriverFSM.changed)
    dp.register_message_handler(update_driver_data, state=ChangeDataDriverFSM.data)

    dp.register_message_handler(orders_by_republic, lambda mes: mes.text == 'По республике')
    dp.register_message_handler(status_order, state=OrdersByRepublicFSM.republic)
    dp.register_message_handler(orders_by_data, state=OrdersByRepublicFSM.status)

    dp.register_message_handler(order_by_id, lambda mes: mes.text == 'По id')
    dp.register_message_handler(order_by_id_answer, state=OrderByIdFSM.id)

    dp.register_callback_query_handler(change_status_to_withdraw, state=WithdrawFSM.id_withdraw)#inline.withdraw.filter(data='change_withdraw'))
    dp.register_message_handler(update_status_to_withdraw, state=WithdrawFSM.status)
