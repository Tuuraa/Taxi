import asyncio

import bot.keyboards.inline as inline
import bot.Database.methods.update as db_update
from bot.env import *


class Countdown:

    def __init__(self, name, id_count_down, driver_id, user_id,
                 loop, step=30, canceled_time=900, time_for_add_paid=180,
                 paid_sum=7, warning_time=300, reminder_time=600, *args, **kwargs):

        self.user_id, self.driver_id = user_id, driver_id
        self.name, self.id = name, id_count_down
        self.loop, self.time_for_add_paid = loop, time_for_add_paid
        self.paid_sum, self.step = paid_sum, step
        self.canceled_time = canceled_time
        self.warning_time, self.reminder_time = warning_time, reminder_time

        self.total_second = 0
        self.total_sum = 0

        self.args = args
        self.kwargs = kwargs

        self.count_down = loop.create_task(self.run_count_down())

    async def run_count_down(self):
        while True:

            await asyncio.sleep(self.step)
            self.total_second += self.step

            if self.total_second == self.warning_time:
                await bot.send_message(
                    self.user_id,
                    "Ваше бесплатное ожидание вышло.\n"
                    "Далее каждую минуту к стоимости заказа будет начисляться по 7 руб."
                )

            if self.total_second == self.reminder_time:
                await bot.send_message(
                    self.user_id,
                    "Прошло уже 10 минут.\n"
                    "Вам осталось 5 мин. Просим поторопиться, "
                    "иначе заказ будет отменен, и с вашего баланса спишется 150 руб."
                )

            if self.total_second > self.time_for_add_paid \
                    and self.total_second % 60 == 0:
                self.total_sum += self.paid_sum

            if self.total_second >= self.canceled_time:
                await self.time_is_up()

    async def time_is_up(self):
        self.count_down.cancel()

        await db_update.remove_balance_from_user(150, self.user_id)
        await db_update.change_status_to_order("CANCELED", self.id)

        await bot.send_message(
            self.driver_id,
            "Время ожидания пассажира вышло. \n"
            "Заказ был автоматически отменен."
        )

        await bot.send_message(
            self.user_id,
            "Время вашего ожидания вышло.\n"
            "С вашего счета было списано 150 руб."
            "Предупреждаем, что для дальнейшего вызова "
            "такси вам надо пополнить кошелек бота на данную сумму",
            reply_markup=inline.profile_driver_btn()
        )

        return {
            "driver_id": self.driver_id,
            "user_id": self.user_id
        }

    def close_coroutine(self):
        self.count_down.cancel()

        return {
            "total_sum": self.total_sum,
            "total_second": self.total_second,
            "driver_id": self.driver_id,
            "user_id": self.user_id
        }

    def __eq__(self, other):

        if isinstance(other, Countdown):

            return self.name == other.name and self.driver_id == other.driver_id \
                and self.user_id == other.user_id

        return NotImplemented
