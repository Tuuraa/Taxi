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
    current_delivery_location = State()
    delivery_order_location = State()
    order_location = State()
    agreed_location = State()
    disagree_location = State()
    delivery_distance = State()
    distance = State()
    time = State()
    delivery_time = State()
    delivery_amount = State()
    amount = State()
    republic = State()
    type_pay = State()
    delivery_type_pay = State()


class CreateRequestWithdrowFSM(StatesGroup):
    type_bank = State()
    card = State()
    amount = State()


class TopUpFSM(StatesGroup):
    amount = State()


class ChangeRepublicFSM(StatesGroup):
    republic = State()