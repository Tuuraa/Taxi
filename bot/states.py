from aiogram.dispatcher.filters.state import State, StatesGroup


class DriverFSM(StatesGroup):
    car_mark = State()
    car_numbers = State()
    phone = State()


class PassengerFSM(StatesGroup):
    phone = State()



