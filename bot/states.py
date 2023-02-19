from aiogram.dispatcher.filters.state import State, StatesGroup


class DriverFSM(StatesGroup):
    car_mark = State()
    car_numbers = State()
    full_name = State()
    republic = State()
    phone = State()


class PassengerFSM(StatesGroup):
    full_name = State()
    phone = State()


class UserLocationFSM(StatesGroup):
    current_location = State()
    order_location = State()
    agreed_location = State()
    disagree_location = State()


class CreateRequestWithdrowFSM(StatesGroup):
    type_bank = State()
    card = State()
    amount = State()
