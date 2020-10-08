from typing import Dict

from aiogram.dispatcher.filters import CommandStart
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, Message
from aiogram.utils.callback_data import CallbackData

from config import JSON_DATA_FILENAME
from functions import read_json_data
from load_all import dp

deposit_cb = CallbackData('deposit', 'club')


@dp.message_handler(CommandStart())
async def start_cmd_handler(message: Message):
    # args = message.get_args() if hasattr(message, 'get_args') else None
    # зарегистрировать пользователя с данными из диплинка

    data = read_json_data(JSON_DATA_FILENAME)
    if data != 'File not read' and data.get('Clubs'):
        for club in data.get('Clubs'):
            keyboard_markup = InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text='Продолжить',
                                          callback_data=deposit_cb.new(club=club.get('Club_name')))]]
            )
            await message.answer(f'Пополнить для клуба {club.get("Club_name")}', reply_markup=keyboard_markup)
    else:
        keyboard_markup = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text='Контакты для связи',
                                      callback_data='contacts')]]
        )
        await message.answer('В данный момент сервис не доступен, попробуйте позднее.', reply_markup=keyboard_markup)


@dp.callback_query_handler(deposit_cb.filter())
async def deposit(call: CallbackQuery, callback_data: Dict[str, str]):
    await call.answer()
    # в следующем окне отправляем уведомление в чат.
    club = callback_data.get('club')
    await call.message.answer(club)
