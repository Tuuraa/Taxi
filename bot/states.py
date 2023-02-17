from aiogram.dispatcher.filters.state import State, StatesGroup


class LogInFSM(StatesGroup):
    phone = State()
