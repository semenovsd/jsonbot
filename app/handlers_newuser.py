from aiogram.dispatcher import FSMContext
from aiogram.types import (CallbackQuery, InlineKeyboardButton,
                           InlineKeyboardMarkup, Message)

from database import User
from filters import is_new_user
from functions import replace_number
from load_all import bot, dp
from states import Newbie


@dp.callback_query_handler(text='cancel_reg', state='*')
async def cancel(call: CallbackQuery, state: FSMContext):
    await bot.delete_message(call.from_user.id, call.message.message_id)
    await state.finish()
    keyboard_markup = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text='Назад', callback_data='demo_task')]]
    )
    reply = 'Очень жаль, что ты не дошёл до конца!'
    await call.message.answer(text=reply, reply_markup=keyboard_markup)


@dp.callback_query_handler(is_new_user, text='new_user')
async def new_user(call: CallbackQuery):
    await call.answer()
    # await call.message.edit_reply_markup()
    await Newbie.Name.set()
    keyboard_markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Отмена', callback_data='cancel_reg')],
        ]
    )
    reply = 'Для начала давай познакомимся. Как тебя зовут?'
    await call.message.answer(text=reply, reply_markup=keyboard_markup)


@dp.message_handler(state=Newbie.Name)
async def user_name(message: Message, state: FSMContext):
    # await message.edit_reply_markup()
    keyboard_markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Отмена', callback_data='cancel_admin')],
        ]
    )
    name = message.text
    if name and len(name) <= 50:
        await Newbie.Gender.set()
        await state.update_data(name=name)
        reply = f'Приятно познакомиться, {name}!\n' \
                f'Твой пол?\U0001F447'
        keyboard_markup.add(
            InlineKeyboardButton(text='\U0001F468', callback_data='man'),
            InlineKeyboardButton(text='\U0001F469', callback_data='woman'),
        )
    else:
        reply = 'К сожалению, слишком длинное имя, не более 50 символов, введи ещё раз.'
    await message.answer(text=reply, reply_markup=keyboard_markup)


@dp.callback_query_handler(state=Newbie.Gender)
async def user_gender(call: CallbackQuery, state: FSMContext):
    await call.answer()
    keyboard_markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Отмена', callback_data='cancel_admin')],
        ]
    )
    gender = call.data
    await Newbie.Age.set()
    await state.update_data(gender=gender)
    reply = f'Отлично!\n' \
            f'Сколько тебе лет?'
    await call.message.answer(text=reply, reply_markup=keyboard_markup)


@dp.message_handler(state=Newbie.Age)
async def user_age(message: Message, state: FSMContext):
    keyboard_markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Отмена', callback_data='cancel_admin')],
        ]
    )
    age = message.text
    if age.isdigit() and len(age) <= 3:
        await state.update_data(age=age)
        await Newbie.Height.set()
        reply = 'Какой у тебя вес сейчас? Укажи цифрами в кг.'
    else:
        reply = 'Укажи пожалуйста возраст в цифрах. Например 21'
    await message.answer(text=reply, reply_markup=keyboard_markup)


@dp.message_handler(state=Newbie.Height)
async def user_height(message: Message, state: FSMContext):
    # await message.edit_reply_markup()
    keyboard_markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Отмена', callback_data='cancel_admin')],
        ]
    )
    height = message.text
    if height.isdigit() and len(height) <= 3:
        await state.update_data(height=height)
        await Newbie.Weight.set()
        reply = 'Какой у тебя рост? Напиши цифрами в сантиметрах.'
    else:
        reply = 'Пожалуйста укажи весь только цифрами.'
    await message.answer(text=reply, reply_markup=keyboard_markup)


@dp.message_handler(state=Newbie.Weight)
async def user_weight(message: Message, state: FSMContext):
    # await message.edit_reply_markup()
    keyboard_markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Отмена', callback_data='cancel_admin')],
        ]
    )
    weight = message.text
    if weight.isdigit() and len(weight) <= 3:
        await state.update_data(weight=weight)
        await Newbie.Lifestyle.set()
        # TODO make goals list
        keyboard_markup.add(InlineKeyboardButton(text='Набрать вес', callback_data='get_mass'))
        keyboard_markup.add(InlineKeyboardButton(text='Похудеть', callback_data='lose_fat'))
        keyboard_markup.add(InlineKeyboardButton(text='Сохранить текущий вес', callback_data='stay_form'))
        reply = 'Отлично! Какая у тебя сейчас цель в тренировках? Выбери нужные вариант.'
    else:
        reply = 'Пожалуйста укажи весь только цифрами.'
    await message.answer(text=reply, reply_markup=keyboard_markup)


@dp.callback_query_handler(state=Newbie.Lifestyle)
async def user_goal(call: CallbackQuery, state: FSMContext):
    await call.answer()
    keyboard_markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Отмена', callback_data='cancel_admin')],
        ]
    )
    await state.update_data(goal=call.data)
    await Newbie.Goal.set()
    reply = 'Хорошая цель! Какой у тебя образ жизни?'
    keyboard_markup.add(InlineKeyboardButton(text='Не очень подвижный', callback_data='sedentary'))
    keyboard_markup.add(InlineKeyboardButton(text='Малоподвижный', callback_data='low'))
    keyboard_markup.add(InlineKeyboardButton(text='Подвижный', callback_data='active'))
    keyboard_markup.add(InlineKeyboardButton(text='Очень подвижный', callback_data='very_active'))
    await call.message.answer(text=reply, reply_markup=keyboard_markup)


@dp.callback_query_handler(state=Newbie.Goal)
async def user_goal(call: CallbackQuery, state: FSMContext):
    await call.answer()
    keyboard_markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Отмена', callback_data='cancel_admin')],
        ]
    )
    await state.update_data(lifestyle=call.data)
    await Newbie.Place.set()
    reply = 'Хорошая цель! Ты будешь заниматсья дома или в зале?'
    keyboard_markup.add(
        InlineKeyboardButton(text='Дома', callback_data='home_training'),
        InlineKeyboardButton(text='В зале', callback_data='workout_training'),
    )
    await call.message.answer(text=reply, reply_markup=keyboard_markup)


@dp.callback_query_handler(text='workout_training', state=Newbie.Place)
async def workout_training(call: CallbackQuery, state: FSMContext):
    await call.answer()
    keyboard_markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Отмена', callback_data='cancel_admin')],
        ]
    )
    place = call.data
    await Newbie.PhoneNumber.set()
    await state.update_data(place=place)
    reply = f'Подскажи свой номер телефона для связи с трениром по телефону.'
    await call.message.answer(text=reply, reply_markup=keyboard_markup)


@dp.callback_query_handler(text='home_training', state=Newbie.Place)
async def home_training(call: CallbackQuery, state: FSMContext):
    await call.answer()
    # await message.edit_reply_markup()
    keyboard_markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Отмена', callback_data='cancel_admin')],
        ]
    )
    place = call.data
    await Newbie.HomeStuff.set()
    await state.update_data(place=place)
    keyboard_markup.add(
        InlineKeyboardButton(text='Есть оборудование', callback_data='home_stuff_exist'),
        InlineKeyboardButton(text='Без оборудования', callback_data='home_stuff_no_exist'),
    )
    reply = f'У тебя есть оборудование дома или подготовить тренировку для которой даже коврик не потрубется?'
    await call.message.answer(text=reply, reply_markup=keyboard_markup)


@dp.callback_query_handler(state=Newbie.HomeStuff)
async def user_home_stuff(call: CallbackQuery, state: FSMContext):
    await call.answer()
    # await message.edit_reply_markup()
    keyboard_markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Отмена', callback_data='cancel_admin')],
        ]
    )
    home_stuff = call.data
    await Newbie.PhoneNumber.set()
    await state.update_data(home_stuff=home_stuff)
    reply = f'Подскажи свой номер телефона для связи с трениром по телефону.'
    await call.message.answer(text=reply, reply_markup=keyboard_markup)


@dp.message_handler(state=Newbie.PhoneNumber)
async def user_phone_number(message: Message, state: FSMContext):
    # await message.edit_reply_markup()
    keyboard_markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Отмена', callback_data='cancel_admin')],
        ]
    )
    phone_number = message.text
    phone_number = replace_number(phone_number)
    if phone_number.isdigit() and len(phone_number) == 11:
        await state.update_data(phone_number=phone_number)
        await Newbie.Email.set()
        reply = 'Лишний раз звонить не будет, можем написать =) Укажи свой email'
    else:
        reply = 'Пожалуйста укажи свой номер телефона только цифрами, в формате 89211234565 или +79211234565'
    await message.answer(text=reply, reply_markup=keyboard_markup)


@dp.message_handler(state=Newbie.Email)
async def user_email(message: Message, state: FSMContext):
    # await message.edit_reply_markup()
    keyboard_markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Отмена', callback_data='cancel_admin')],
        ]
    )
    email = message.text
    if email.find('@'):
        keyboard_markup.add(InlineKeyboardButton(text='Записать', callback_data='save_reg_user'))
        await state.update_data(email=email)
        await Newbie.Confirm.set()
        async with state.proxy() as data:
            name = data['name']
            gender = data['gender']
            age = data['age']
            height = data['height']
            weight = data['weight']
            goal = data['goal']
            lifestyle = data['lifestyle']
            place = data['place']
            home_stuff = data['home_stuff']
            phone_number = data['phone_number']
        reply = 'Давай всё проверим:\n' \
                f'Твоё имя {name} и тебе {age} лет, пол {gender}. \n' \
                f'Твоя цель {goal}, образ жизни {lifestyle}, а параметры рост {weight} и вес {height}\n' \
                f'Ты будешь заниматься {place}\n' \
                f'А для дополнительнйо связи телефон {phone_number} и почта {email}\n' \
                f'Всё правильно? Тогда нажимай зарегистрировать!'
    else:
        reply = 'Пожалуйста укажи свой email, в формате example@example.ru'
    await message.answer(text=reply, reply_markup=keyboard_markup)


@dp.callback_query_handler(text='save_reg_user', state=Newbie.Confirm)
async def save_reg_user(call: CallbackQuery, state: FSMContext, user: User):
    # await call.message.edit_reply_markup()
    async with state.proxy() as data:
        await user.update(
            name=data['name'],
            gender=data['gender'],
            age=data['age'],
            height=data['height'],
            weight=data['weight'],
            goal=data['goal'],
            lifestyle=data['lifestyle'],
            place=data['place'],
            home_stuff=data['home_stuff'],
            phone_number=data['phone_number'],
            email=data['email'],
            registered=True
        ).apply()
    await state.finish()
    keyboard_markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='На главную', callback_data='main')],
        ]
    )
    reply = 'Поздравляю! Теперь тебе доступны все возможности Тренера Феди! ' \
            'Переходи в главное меню, чтобы подробнее узнать о них!'
    await call.message.answer(text=reply, reply_markup=keyboard_markup)

# TODO add question who many trainings in week?
