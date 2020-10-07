from typing import Dict, Union

from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, Message
from aiogram.utils.callback_data import CallbackData

from config import TG_ADMINS_ID
from database import User, TrainingPlan, Section
from load_all import dp, bot
from states import AddPlan, PlanDetails

plan_view_cb = CallbackData('p_v', 'name')
view_day_plan_cb = CallbackData('d_v', 'day')
plan_day_cb = CallbackData('task', 'action', 'day')


@dp.message_handler(state='*', commands='plan_task_cancel')
@dp.callback_query_handler(state='*', text='plan_task_cancel')
async def cancel_handler(message: Union[Message, CallbackQuery], state: FSMContext):
    current_state = await state.get_state()
    if current_state:
        # Cancel state
        await state.finish()

    await bot.delete_message(message.from_user.id, message.message.message_id)

    keyboard_markup = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text='Меню программ', callback_data='plans')]]
    )
    await bot.send_message(message.from_user.id,
                           text='Отменено. Вернитесь в админское меню.',
                           reply_markup=keyboard_markup)


@dp.callback_query_handler(text='plans', user_id=TG_ADMINS_ID)
async def plans(call: CallbackQuery):
    await call.answer()

    keyboard_markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Назад', callback_data='admin')],
            [InlineKeyboardButton(text='Добавить',
                                  callback_data='add_plan')],
            [InlineKeyboardButton(text='Просмотр',
                                  callback_data='view_plans')],
        ]
    )
    reply = f'Добавить или посмотреть?'
    await call.message.answer(reply, reply_markup=keyboard_markup)


@dp.callback_query_handler(text='add_plan', user_id=TG_ADMINS_ID)
async def add_plan(call: CallbackQuery):
    await call.answer()
    await AddPlan.Name.set()
    keyboard_markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Отмена', callback_data='admin_cancel')],
        ]
    )

    reply = f'Как будет называться план?'
    await call.message.answer(reply, reply_markup=keyboard_markup)


@dp.message_handler(state=AddPlan.Name)
async def add_plan_name(message: Message, state: FSMContext):
    keyboard_markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Отмена', callback_data='cancel_admin')],
        ]
    )
    name = message.text
    if name and len(name) <= 64:
        await AddPlan.Gender.set()
        await state.update_data(name=name)
        reply = f'План тренировок для мальчиков или девочек?'
        keyboard_markup.add(
            InlineKeyboardButton(text='\U0001F468', callback_data='man'),
            InlineKeyboardButton(text='\U0001F469', callback_data='woman'),
        )
    else:
        reply = 'К сожалению, слишком длинное имя, не более 64 символов, введи ещё раз.'
    await message.answer(text=reply, reply_markup=keyboard_markup)


@dp.callback_query_handler(state=AddPlan.Gender)
async def plan_gender(call: CallbackQuery, state: FSMContext):
    await call.answer()
    keyboard_markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Отмена', callback_data='cancel_admin')],
        ]
    )
    gender = call.data
    await state.update_data(gender=gender)
    await AddPlan.Goal.set()
    keyboard_markup.add(InlineKeyboardButton(text='Набрать вес', callback_data='get_mass'))
    keyboard_markup.add(InlineKeyboardButton(text='Похудеть', callback_data='lose_fat'))
    keyboard_markup.add(InlineKeyboardButton(text='Сохранить текущий вес', callback_data='stay_form'))
    reply = f'Для каких целей?'
    await call.message.answer(text=reply, reply_markup=keyboard_markup)


@dp.callback_query_handler(state=AddPlan.Goal)
async def add_plan_goal(call: CallbackQuery, state: FSMContext):
    keyboard_markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Отмена', callback_data='cancel_admin')],
        ]
    )
    goal = call.data
    await state.update_data(goal=goal)
    await AddPlan.Lifestyle.set()
    keyboard_markup.add(InlineKeyboardButton(text='Не очень подвижный', callback_data='sedentary'))
    keyboard_markup.add(InlineKeyboardButton(text='Малоподвижный', callback_data='low'))
    keyboard_markup.add(InlineKeyboardButton(text='Подвижный', callback_data='active'))
    keyboard_markup.add(InlineKeyboardButton(text='Очень подвижный', callback_data='very_active'))
    reply = f'Для какого образа жизни?'
    await call.message.answer(text=reply, reply_markup=keyboard_markup)


@dp.callback_query_handler(state=AddPlan.Lifestyle)
async def add_plan_goal(call: CallbackQuery, state: FSMContext):
    keyboard_markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Отмена', callback_data='cancel_admin')],
        ]
    )
    lifestyle = call.data
    await state.update_data(lifestyle=lifestyle)
    await AddPlan.Place.set()
    keyboard_markup.add(
        InlineKeyboardButton(text='Дома', callback_data='home_training'),
        InlineKeyboardButton(text='В зале', callback_data='workout_training'),
    )
    reply = f'Для зала или дома?'
    await call.message.answer(text=reply, reply_markup=keyboard_markup)


@dp.callback_query_handler(text='workout_training', state=AddPlan.Place)
async def workout_training(call: CallbackQuery, state: FSMContext):
    await call.answer()
    keyboard_markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Отмена', callback_data='cancel_admin')],
        ]
    )
    place = call.data
    await AddPlan.Description.set()
    await state.update_data(place=place)
    reply = f'Введи описание для данной программы'
    await call.message.answer(text=reply, reply_markup=keyboard_markup)


@dp.callback_query_handler(text='home_training', state=AddPlan.Place)
async def home_training(call: CallbackQuery, state: FSMContext):
    await call.answer()
    keyboard_markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Отмена', callback_data='cancel_admin')],
        ]
    )
    place = call.data
    await AddPlan.HomeStuff.set()
    await state.update_data(place=place)
    keyboard_markup.add(
        InlineKeyboardButton(text='С оборудованием', callback_data='home_stuff_exist'),
        InlineKeyboardButton(text='Без оборудования', callback_data='home_stuff_no_exist'),
    )
    reply = f'План для тенировок с оборудованием или без?'
    await call.message.answer(text=reply, reply_markup=keyboard_markup)


@dp.callback_query_handler(state=AddPlan.HomeStuff)
async def plan_home_stuff(call: CallbackQuery, state: FSMContext):
    await call.answer()
    keyboard_markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Отмена', callback_data='cancel_admin')],
        ]
    )
    home_stuff = call.data
    await AddPlan.Description.set()
    await state.update_data(home_stuff=home_stuff)
    reply = f'Введи описание для данной программы'
    await call.message.answer(text=reply, reply_markup=keyboard_markup)


@dp.message_handler(state=AddPlan.Description)
async def add_plan_description(message: Message, state: FSMContext, user: User):
    keyboard_markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Отмена', callback_data='cancel_admin')],
            [InlineKeyboardButton(text='Сохранить', callback_data='save_plan')],

        ]
    )
    description = message.text
    if description and len(description) <= 256:
        await AddPlan.Confirm.set()
        await state.update_data(description=description, author=user.user_id)
        data = await state.get_data()
        name = data.get('name')
        gender = data.get('gender')
        goal = data.get('goal')
        lifestyle = data.get('lifestyle')
        place = data.get('place')
        home_stuff = data.get('home_stuff')
        description = data.get('description')
        reply = f'План будет называться: {name}\n' \
                f'Расчитан на: {gender}\n' \
                f'Для цели: {goal}\n' \
                f'Под стиль жизни: {lifestyle}\n' \
                f'Для занятий: {place} с/без инвентаря: {home_stuff}\n' \
                f'Описание плана: {description}\n\n\n' \
                f'Если всё правильно нажми Сохранить.'
    else:
        reply = 'К сожалению, слишком длинное описание, не более 256 символов, введи ещё раз.'
    await message.answer(text=reply, reply_markup=keyboard_markup)


@dp.callback_query_handler(state=AddPlan.Confirm, text='save_plan')
async def save_plan(call: CallbackQuery, state: FSMContext):
    await call.answer()
    data = await state.get_data()
    await state.finish()
    await TrainingPlan.add(data)
    keyboard_markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Админ панель', callback_data='admin')],
            [InlineKeyboardButton(text='Просмотр тренировок',
                                  callback_data='view_plans')],
            [InlineKeyboardButton(text='Добавить ещё',
                                  callback_data='add_plan')],
        ]
    )
    reply = f'Что дальше?'
    await call.message.answer(reply, reply_markup=keyboard_markup)


@dp.callback_query_handler(text='view_plans', state='*')
async def add_plan(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await state.finish()
    keyboard_markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Назад', callback_data='plans')],
        ]
    )

    plans_name = await TrainingPlan.get_all_names()
    for plan_name in plans_name:
        keyboard_markup.add(
            InlineKeyboardButton(text=plan_name,
                                 callback_data=plan_view_cb.new(name=plan_name)),
        )

    reply = f'Вот список планов тенировок:'
    await call.message.answer(reply, reply_markup=keyboard_markup)


@dp.callback_query_handler(plan_view_cb.filter(), state='*')
async def plan_view(call: CallbackQuery, callback_data: Dict[str, str], state: FSMContext):
    await call.answer()

    await PlanDetails.ChoiceDay.set()
    plan_name = callback_data.get('name')
    plan = await TrainingPlan.get_plan(plan_name)
    await state.update_data(plan_name=plan_name, plan=plan)

    keyboard_markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Назад', callback_data='view_plans')],
            [InlineKeyboardButton(text=f'Понедельник',
                                  callback_data=view_day_plan_cb.new(day='monday'))],
            [InlineKeyboardButton(text=f'Вторник',
                                  callback_data=view_day_plan_cb.new(day='tuesday'))],
            [InlineKeyboardButton(text=f'Среда',
                                  callback_data=view_day_plan_cb.new(day='wednesday'))],
            [InlineKeyboardButton(text=f'Четверг',
                                  callback_data=view_day_plan_cb.new(day='thursday'))],
            [InlineKeyboardButton(text=f'Пятница',
                                  callback_data=view_day_plan_cb.new(day='friday'))],
            [InlineKeyboardButton(text=f'Суббота',
                                  callback_data=view_day_plan_cb.new(day='saturday'))],
            [InlineKeyboardButton(text=f'Воскресенье',
                                  callback_data=view_day_plan_cb.new(day='sunday'))],
        ]
    )
    reply = f'Какой день недели?'
    await call.message.answer(reply, reply_markup=keyboard_markup)


@dp.callback_query_handler(view_day_plan_cb.filter(), state=PlanDetails.ChoiceDay)
async def plan_day_view(call: CallbackQuery, callback_data: Dict[str, str], state: FSMContext):
    await call.answer()

    data = await state.get_data()
    plan = data.get('plan')
    plan_name = data.get('plan_name')
    day_name = callback_data.get('day')
    day = plan.view_day(day_name)
    await state.update_data(day=day, day_name=day_name)

    keyboard_markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Назад', callback_data=plan_view_cb.new(name=plan_name))],
            [InlineKeyboardButton(text='Добавить комплекс', callback_data=plan_day_cb.new(action='add', day=day_name))],
        ]
    )

    # if day:
    #     for task in day:
    #         keyboard_markup.add(
    #             InlineKeyboardButton(text='\u274C',
    #                                  callback_data=plan_day_cb.new(action='del', day=day_name)),
    #             InlineKeyboardButton(text=f'{task.time} - {task.name}',
    #                                  callback_data=plan_day_cb.new(action='view', day=day_name)),
    #             InlineKeyboardButton(text='\u270F',
    #                                  callback_data=plan_day_cb.new(action='edit', day=day_name)),
    #         )

    reply = f'Расписание на {day_name}:'
    await call.message.answer(reply, reply_markup=keyboard_markup)













@dp.callback_query_handler(plan_day_cb.filter(action='add'), state=PlanDetails.ChoiceDay)
async def plan_day_view(call: CallbackQuery, callback_data: Dict[str, str], state: FSMContext):
    await call.answer()

# TODO Reset incoming state data!
    data = await state.get_data()
    plan = data['plan']
    day = data['day']
    await PlanDetails.AddTask.set()

    sections = await Section.get_all_names()
    # await call.message.answer(sections)
    keyboard_markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Отмена', callback_data='plan_task_cancel')],
        ]
    )

    if sections:
        for section in sections:
            keyboard_markup.add(
                InlineKeyboardButton(text=section.name, callback_data=section.name)
            )

    reply = f'Из какого раздела будет комплекс?'
    await call.message.answer(reply, reply_markup=keyboard_markup)


@dp.callback_query_handler(state=PlanDetails.AddTask)
async def save_plan(call: CallbackQuery, state: FSMContext):
    await call.answer()
    section_name = call.data
    await state.update_data(section_name=section_name)
    await PlanDetails.AddTaskName.set()

    keyboard_markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Отмена', callback_data='plan_task_cancel')],
        ]
    )
    reply = f'Напиши название комплекса:'
    await call.message.answer(reply, reply_markup=keyboard_markup)


@dp.message_handler(state=PlanDetails.AddTaskName)
async def plan_details_time(message: Message, state: FSMContext, user: User):
    keyboard_markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Отмена', callback_data='cancel_admin')],
        ]
    )
    task_name = message.text
    if task_name and len(task_name) <= 64:
        await state.update_data(task_name=task_name)
        await PlanDetails.AddTaskTime.set()
        reply = f'На какое время добавить комплекс? Укажи в формате ЧЧ:ММ, например 16:00'
    else:
        reply = 'К сожалению, слишком длинное название, не более 64 символов, введи ещё раз.'
    await message.answer(text=reply, reply_markup=keyboard_markup)


@dp.message_handler(state=PlanDetails.AddTaskTime)
async def add_plan_description(message: Message, state: FSMContext, user: User):
    keyboard_markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Отмена', callback_data='cancel_admin')],
            [InlineKeyboardButton(text='Сохранить', callback_data='save_plan_task')],
        ]
    )
    task_time = message.text
    if task_time and len(task_time) == 5:

        await PlanDetails.ConfirmAddTask.set()
        await state.update_data(task_time=task_time, task_author=user.user_id)
        data = await state.get_data()
        task_name = data.get('task_name')
        task_section = data.get('task_section')
        day = data.get('day')

        reply = f'Комплекс {task_name} под {task_section} будет добавлен на {day} в {task_time}\n\n\n' \
                f'Если всё верно нажми сохранить!'
    else:
        reply = 'Неправильный формат времени, укажи в формате ЧЧ:ММ, например 16:00'
    await message.answer(text=reply, reply_markup=keyboard_markup)


@dp.callback_query_handler(state=PlanDetails.ConfirmAddTask, text='save_plan_task')
async def mange_topic(call: CallbackQuery, state: FSMContext):

    await call.answer()
    data = await state.get_data()
    await TrainingPlan.add_task(data)
    day = data.get('day')
    plan = data.get('plan')

    keyboard_markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Тренировки', callback_data='plans')],
            [InlineKeyboardButton(text='Перейти к другим дням',
                                  callback_data=plan_view_cb.new(name=plan.name))],
            [InlineKeyboardButton(text=f'Добавить ещё {day}',
                                  callback_data=plan_day_cb.new(action='add', day=day))],
        ]
    )
    reply = f'Что дальше?'
    await call.message.answer(reply, reply_markup=keyboard_markup)




