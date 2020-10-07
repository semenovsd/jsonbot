"""Аутентификация пользователей — проверяем есть ли пользователь с таким телеграмм ID в бд"""
from aiogram import types
from aiogram.dispatcher.middlewares import BaseMiddleware

from database import User


class AccessMiddleware(BaseMiddleware):

    def __init__(self):
        super().__init__()

    async def on_pre_process_message(self, message: types.Message, data: dict):
        data['user'] = await User().get_or_create(types.User.get_current().id)

    async def on_pre_process_callback_query(self, callback_query: types.CallbackQuery, data: dict):
        data['user'] = await User().get_or_create(types.User.get_current().id)

    async def on_pre_process_pre_checkout_query(self, checkout_query: types.PreCheckoutQuery, data: dict):
        data['user'] = await User().get_or_create(types.User.get_current().id)