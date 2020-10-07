from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import CommandStart
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, Message

from filters import is_new_user, is_reg_user
from load_all import bot, dp


@dp.message_handler(CommandStart(), state='*')
async def start_cmd_handler(message: Message, state: FSMContext):
    # Cancel any state
    await state.finish()
    keyboard_markup = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text='Продолжить', callback_data='main')]]
    )
    reply = 'Добропожаловать! Нажми продолжить!'
    await bot.send_message(message.from_user.id, text=reply, reply_markup=keyboard_markup)


# Main screen
@dp.callback_query_handler(is_new_user, text='main')
async def users_help(call: CallbackQuery):
    keyboard_markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Зарегистрироваться', callback_data='new_user')],
        ]
    )
    reply = 'Добропожаловать! Я тренер Федя, помогу в достижение твоих целей! \n' \
            'Чтобы я лучше знал как тебе помочь, пройди быструю регистрацию.'
    await call.message.answer(text=reply, reply_markup=keyboard_markup)


@dp.callback_query_handler(is_reg_user, text='main')
async def users_help(call: CallbackQuery):
    await call.answer()
    keyboard_markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Личный кабинет', callback_data='new_user')],
        ]
    )
    reply = 'Теперь я расскажу как могу помочь тебе с тренировками! Выбери с чего начнём.'
    await call.message.answer(text=reply, reply_markup=keyboard_markup)
