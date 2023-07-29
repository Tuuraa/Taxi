import asyncio


class Countdown:

    def __init__(self, name, id_count_down, driver_id, user_id,
                 loop, step=30, canceled_time=900, time_for_add_paid=180,
                 paid_sum=7, *args, **kwargs):

        self.user_id, self.driver_id = user_id, driver_id
        self.name, self.id = name, id_count_down
        self.loop, self.time_for_add_paid = loop, time_for_add_paid
        self.paid_sum, self.step = paid_sum, step
        self.canceled_time = canceled_time

        self.total_second = 0
        self.total_sum = 0

        self.args = args
        self.kwargs = kwargs

        print("create task")
        self.count_down = loop.create_task(self.run_count_down())

    async def run_count_down(self):
        print("start task")
        while True:

            print(self.name, self.driver_id,
                  f'{self.canceled_time - self.total_second} second left', '\n')
            await asyncio.sleep(self.step)
            self.total_second += self.step

            if self.total_second > self.time_for_add_paid \
                    and self.total_second % 60 == 0:
                self.total_sum += self.paid_sum

            if self.total_second >= self.canceled_time:
                self.time_is_up()

    def time_is_up(self):
        self.count_down.cancel()
        print("time is over")
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
