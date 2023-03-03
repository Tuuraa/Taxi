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
    distance = State()
    republic = State()
    type_pay = State()
    time = State()
    amount = State()


class DeliveryFSM(StatesGroup):
    current_delivery_location = State()
    delivery_order_location = State()
    delivery_time = State()
    delivery_amount = State()
    delivery_distance = State()
    republic = State()
    delivery_type_pay = State()


class CreateRequestWithdrowFSM(StatesGroup):
    type_bank = State()
    card = State()
    amount = State()


class TopUpFSM(StatesGroup):
    amount = State()


class ChangeRepublicFSM(StatesGroup):
    republic = State()


class SearchPassengerFSM(StatesGroup):
    name = State()


class SearchDriverFSM(StatesGroup):
    name = State()


class ChangeDataUserFSM(StatesGroup):
    user_id = State()
    changed = State()
    data = State()


class ChangeDataDriverFSM(StatesGroup):
    user_id = State()
    changed = State()
    data = State()
