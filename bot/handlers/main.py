from aiogram import Dispatcher
from .user import register_user_hanlers
from .admin import register_admin_handlers


def register_all_handlers(dp:Dispatcher):
    register_user_hanlers(dp)
    register_admin_handlers(dp)
