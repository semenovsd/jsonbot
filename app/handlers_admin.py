from asyncio import sleep
from typing import Union, Dict

from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, Message, ContentType
from aiogram.utils.callback_data import CallbackData

from config import TG_ADMINS_ID
from database import User, Trainer, Section, Note
from functions import send_messages
from load_all import bot, dp
from states import Mailing, AddTopic, EditNote

program_cd = CallbackData('select_program', 'user_id')
user_administrate_cd = CallbackData('user_administrate', 'user_id')
block_cd = CallbackData('block_user', 'id')
manage_cb = CallbackData('manage', 'section', 'action')
topic_cb = CallbackData('add_topic', 'section', 'topic')
topic_view_cb = CallbackData('view_topic', 'section', 'topic')
topic_view_note_cb = CallbackData('view_note', 'section', 'topic', 'note')
topic_edit_note_cb = CallbackData('edit_note', 'section', 'topic', 'note')


# Cancel button for all cases
@dp.message_handler(state='*', commands='admin_cancel')
@dp.callback_query_handler(state='*', text='admin_cancel')
async def cancel_handler(message: Union[Message, CallbackQuery], state: FSMContext):
    current_state = await state.get_state()
    if current_state:
        # Cancel state
        await state.finish()

    await bot.delete_message(message.from_user.id, message.message.message_id)

    keyboard_markup = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text='Меню админа', callback_data='admin')]]
    )
    await bot.send_message(message.from_user.id,
                           text='Отменено. Вернитесь в админское меню.',
                           reply_markup=keyboard_markup)


@dp.message_handler(user_id=TG_ADMINS_ID, commands='admin')
@dp.callback_query_handler(user_id=TG_ADMINS_ID, text='admin')
async def admin_panel(message: Union[Message, CallbackQuery]):
    keyboard_markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Новые пользователи', callback_data='new_users')],
            [InlineKeyboardButton(text='Посмотреть всех пользователей', callback_data='list_users')],
            [InlineKeyboardButton(text='Посмотреть всех тренеров', callback_data='all_coach')],
            [InlineKeyboardButton(text='Сделать рассылку', callback_data='broadcast')],
            [InlineKeyboardButton(text='Пригласить тренера', callback_data='add_coach')],
            [InlineKeyboardButton(text='Тренировки', callback_data='plans')],
            [InlineKeyboardButton(text='Упражнения',
                                  callback_data=manage_cb.new(section='workout', action='mange'))],
            [InlineKeyboardButton(text='Питание',
                                  callback_data=manage_cb.new(section='nutrition', action='mange'))],
            [InlineKeyboardButton(text='Фарма',
                                  callback_data=manage_cb.new(section='pharma', action='mange'))],
            [InlineKeyboardButton(text='Мед. анализы',
                                  callback_data=manage_cb.new(section='medical', action='mange'))],
            [InlineKeyboardButton(text='Добавить событие', callback_data='add_event')],
        ]
    )
    reply = 'Админ панель.'
    await bot.send_message(chat_id=message.from_user.id, text=reply, reply_markup=keyboard_markup)


@dp.callback_query_handler(text='new_users')
async def new_users_list(call: CallbackQuery):
    await call.answer()
    keyboard_markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='назад', callback_data='admin')],
        ]
    )
    reply = f'Список новых пользователей:\n'
    new_users = await User.new_users()
    for user in new_users:
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text='Составить программу тренировок',
                                      callback_data=program_cd.new(user_id=f'{user.user_id}'))],
            ]
        )
        text = f'Пользователь: {user.name} {user.gender} {user.age}\n' \
               f'Рост:{user.height} см, Вес: {user.weight} кг\n' \
               f'Цель:{user.goal}, место: {user.place}, оборудование: {user.home_stuff}\n' \
               f'Контакты: телефон:{user.phone_number}, почта: {user.email}, id:{user.user_id}\n\n\n'
        await call.message.answer(text=text, reply_markup=keyboard)
        await sleep(0.05)
    await call.message.answer(text=reply, reply_markup=keyboard_markup)


# TODO how create training programs ?!
@dp.callback_query_handler(program_cd.filter())
async def select_program(call: CallbackQuery, callback_data: Dict[str, str]):
    await call.answer()
    user_id = callback_data.get('user_id')
    training_user = await User.get_or_create(user_id)
    keyboard_markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='назад', callback_data='admin')],
        ]
    )
    reply = f' Будем составлять программу тренировки для пользователя {training_user.name}'
    await call.message.answer(text=reply, reply_markup=keyboard_markup)


@dp.callback_query_handler(text='list_users')
async def list_users(call: CallbackQuery):
    await call.answer()
    keyboard_markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='назад', callback_data='admin')],
        ]
    )
    reply = f'Список новых пользователей:\n'
    all_users = await User.all_users()
    for user in all_users:
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text='Управлять',
                                      callback_data=user_administrate_cd.new(user_id=f'{user.user_id}'))],
            ]
        )
        text = f'Пользователь: {user.name} {user.gender} {user.age}\n' \
               f'Рост:{user.height} см, Вес: {user.weight} кг\n' \
               f'Цель:{user.goal}, место: {user.place}, оборудование: {user.home_stuff}\n' \
               f'Контакты: телефон:{user.phone_number}, почта: {user.email}, id:{user.user_id}\n\n\n'
        await call.message.answer(text=text, reply_markup=keyboard)
        await sleep(0.05)
    await call.message.answer(text=reply, reply_markup=keyboard_markup)


# TODO how administrate user ?!
@dp.callback_query_handler(user_administrate_cd.filter(), user_id=TG_ADMINS_ID)
async def user_administrate(call: CallbackQuery, callback_data: Dict[str, str]):
    await call.answer()
    user_id = callback_data.get('user_id')
    current_user = await User.get_or_create(user_id)
    keyboard_markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='назад', callback_data='admin')],
            [InlineKeyboardButton(text='Заблокировать', callback_data=block_cd.new(id=current_user.user_id))],
        ]
    )
    reply = f'Тут что то можно сделать с пользователем {current_user.user_id}.'
    await call.message.answer(text=reply, reply_markup=keyboard_markup)


# USERS BROADCAST
@dp.callback_query_handler(user_id=TG_ADMINS_ID, text='broadcast')
async def choice_receiver(call: CallbackQuery):
    await call.answer()
    await Mailing.Receiver.set()
    keyboard_markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Пользователи', callback_data='users')],
            [InlineKeyboardButton(text='Тренера', callback_data='trainers')],
        ]
    )
    await call.message.answer('Для кого сделать рассылку?', reply_markup=keyboard_markup)


@dp.callback_query_handler(user_id=TG_ADMINS_ID, state=Mailing.Receiver)
async def users_broadcast(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await state.update_data(reciever=call.data)
    await bot.send_message(call.from_user.id, text=f'Пришлите текст рассылки для ВСЕХ {call.data}.')
    await Mailing.Text.set()


@dp.message_handler(user_id=TG_ADMINS_ID, state=Mailing.Text)
async def mailing(message: Message, state: FSMContext):
    text = message.text
    await state.update_data(mailing_text=text)
    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Отправить сообщение', callback_data='mailing_start')],
            [InlineKeyboardButton(text='Отмена', callback_data='admin_cancel')],
        ]
    )
    await message.answer(f'Тексты сообщения:\n{message.text}\n Введите повторно текст для редактирования',
                         reply_markup=markup)


@dp.callback_query_handler(user_id=TG_ADMINS_ID, text='mailing_start', state=Mailing.Text)
async def mailing_start(call: CallbackQuery, state: FSMContext):
    await call.answer()
    data = await state.get_data()
    mailing_text = data.get('mailing_text')
    reciever = data.get('reciever')
    await state.finish()
    reciever_list = await User.all_users() if reciever == 'users' else await Trainer.get_all()
    id_list = [user.user_id for user in reciever_list]
    await send_messages(mailing_text, id_list)
    keyboard_markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Назад', callback_data='admin')],
        ]
    )
    await call.message.answer("Рассылка выполнена.", reply_markup=keyboard_markup)


# Add Coach
@dp.callback_query_handler(user_id=TG_ADMINS_ID, text='add_coach')
async def mailing_start(call: CallbackQuery):
    await call.answer()
    bot_username = (await bot.me).username
    token = 'sdklfjskaldfksldjfkdsjgkhldkjss'
    link = f'https://t.me/{bot_username}?invite={token}'
    keyboard_markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Назад', callback_data='admin')],
        ]
    )
    reply = f'Ссылка для приглашения тренера:\n' \
            f'{link}'
    await call.message.answer(reply, reply_markup=keyboard_markup)


# Management
@dp.callback_query_handler(manage_cb.filter(action='mange'), user_id=TG_ADMINS_ID)
async def mange_section(call: CallbackQuery, callback_data: Dict[str, str]):
    await call.answer()
    section = await Section.get(callback_data.get('section'))

    keyboard_markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Назад', callback_data='admin')],
            [InlineKeyboardButton(text='Добавить',
                                  callback_data=manage_cb.new(section=section.name, action='add'))],
            [InlineKeyboardButton(text='Просмотр',
                                  callback_data=manage_cb.new(section=section.name, action='view'))],
        ]
    )
    reply = f'Управление {section.name}'
    await call.message.answer(reply, reply_markup=keyboard_markup)


@dp.callback_query_handler(manage_cb.filter(action='add'), user_id=TG_ADMINS_ID)
async def mange_section(call: CallbackQuery, callback_data: Dict[str, str]):
    await call.answer()
    section = await Section().get(callback_data.get('section'))

    keyboard_markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Отмена', callback_data='admin_cancel')],
        ]
    )
    for topic in section.topics:
        keyboard_markup.add(
            InlineKeyboardButton(text=topic,
                                 callback_data=topic_cb.new(section=section.name, topic=topic)),
        )
    reply = f'В какую группу добавить? {section}\n{section.name}{section.topics}'
    await call.message.answer(reply, reply_markup=keyboard_markup)


@dp.callback_query_handler(topic_cb.filter(), user_id=TG_ADMINS_ID)
async def mange_topic(call: CallbackQuery, callback_data: Dict[str, str], state: FSMContext):
    await call.answer()
    await AddTopic.Name.set()
    await state.update_data(section=callback_data.get('section'),
                            topic=callback_data.get('topic')
                            )
    keyboard_markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Отмена', callback_data='admin_cancel')],
        ]
    )
    reply = f'Как будет называться?'
    await call.message.answer(reply, reply_markup=keyboard_markup)


@dp.message_handler(state=AddTopic.Name, user_id=TG_ADMINS_ID)
async def add_note_name(message: Message, state: FSMContext):
    keyboard_markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Отмена', callback_data='cancel_admin')],
        ]
    )
    note_name = message.text
    if note_name and len(note_name) <= 64:
        await state.update_data(note_name=note_name)
        await AddTopic.Image.set()
        reply = 'Теперь загрузи изображение.'
    else:
        reply = 'Слишком длинное название, пожлауйста не больше 64 символов.'
    await message.answer(text=reply, reply_markup=keyboard_markup)


@dp.message_handler(state=AddTopic.Image, user_id=TG_ADMINS_ID, content_types=ContentType.VIDEO)
async def add_note_image(message: Message, state: FSMContext):
    keyboard_markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Отмена', callback_data='cancel_admin')],
            [InlineKeyboardButton(text='Сохранить', callback_data='save_note')],
        ]
    )
    await state.update_data(image=message.video.file_id)
    await AddTopic.Confirm.set()
    data = await state.get_data()
    section = data.get('section')
    topic = data.get('topic')
    title = data.get('note_name')
    reply = f'Сохранить {section} в разделе {topic} под названием {title}?'
    await message.answer(text=reply, reply_markup=keyboard_markup)


@dp.callback_query_handler(state=AddTopic.Confirm, text='save_note', user_id=TG_ADMINS_ID)
async def mange_topic(call: CallbackQuery, state: FSMContext):
    await call.answer()
    data = await state.get_data()
    section = data.get('section')
    topic = data.get('topic')
    title = data.get('note_name')
    image = data.get('image')
    await state.finish()
    await Note.add(section, topic, title, image)
    keyboard_markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Админ панель', callback_data='admin')],
            [InlineKeyboardButton(text='Управление',
                                  callback_data=manage_cb.new(section=section, action='mange'))],
            [InlineKeyboardButton(text='Добавить ещё',
                                  callback_data=manage_cb.new(section=section, action='add'))],
        ]
    )
    reply = f'Что дальше?'
    await call.message.answer(reply, reply_markup=keyboard_markup)


@dp.callback_query_handler(manage_cb.filter(action='view'), user_id=TG_ADMINS_ID)
async def view_topics(call: CallbackQuery, callback_data: Dict[str, str]):
    await call.answer()
    section = await Section().get(callback_data.get('section'))

    keyboard_markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Назад', callback_data=manage_cb.new(action='mange', section=section.name))],
        ]
    )
    for topic in section.topics:
        keyboard_markup.add(
            InlineKeyboardButton(text=topic,
                                 callback_data=topic_view_cb.new(section=section.name, topic=topic)),
        )
    reply = f'Список подразделов:'
    await call.message.answer(reply, reply_markup=keyboard_markup)


@dp.callback_query_handler(topic_view_cb.filter(), user_id=TG_ADMINS_ID)
async def view_notes(call: CallbackQuery, callback_data: Dict[str, str]):
    await call.answer()
    section = callback_data.get('section')
    topic = callback_data.get('topic')
    notes = await Note.get_all(callback_data.get('section'), callback_data.get('topic'))

    keyboard_markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Назад', callback_data=manage_cb.new(section=section, action='view'))],
        ]
    )

    for note in notes:
        keyboard_markup.add(
            InlineKeyboardButton(text=note.title,
                                 callback_data=topic_view_note_cb.new(section=section, topic=topic, note=note.id)),
        )
    reply = f'Данный подраздел содержит:'
    await call.message.answer(reply, reply_markup=keyboard_markup)


@dp.callback_query_handler(topic_view_note_cb.filter(), user_id=TG_ADMINS_ID)
async def view_note(call: CallbackQuery, callback_data: Dict[str, str]):
    await call.answer()
    section = callback_data.get('section')
    topic = callback_data.get('topic')
    note = await Note.get(callback_data.get('note'))

    keyboard_markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Назад',
                                  callback_data=topic_view_cb.new(section=section, topic=topic))],
            [InlineKeyboardButton(text='Редактировать',
                                  callback_data=topic_edit_note_cb.new(section=section, topic=topic, note=note.id))],
        ]
    )
    reply = f'{note.title}'
    await call.message.answer_video(note.image, caption=reply, width=50, reply_markup=keyboard_markup)


@dp.callback_query_handler(topic_edit_note_cb.filter(), user_id=TG_ADMINS_ID)
async def edit_note_name(call: CallbackQuery, callback_data: Dict[str, str], state: FSMContext):
    await call.answer()
    await EditNote.Name.set()
    await state.update_data(section=callback_data.get('section'),
                            topic=callback_data.get('topic'),
                            note=callback_data.get('note')
                            )
    keyboard_markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Отмена', callback_data='admin_cancel')],
        ]
    )
    reply = f'Введите название:'
    await call.message.answer(reply, reply_markup=keyboard_markup)


@dp.message_handler(state=EditNote.Name, user_id=TG_ADMINS_ID)
async def edit_note_image(message: Message, state: FSMContext):
    keyboard_markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Отмена', callback_data='cancel_admin')],
        ]
    )
    note_name = message.text
    if note_name and len(note_name) <= 64:
        await state.update_data(note_name=note_name)
        await EditNote.Image.set()
        reply = 'Теперь загрузи изображение.'
    else:
        reply = 'Слишком длинное название, пожлауйста не больше 64 символов.'
    await message.answer(text=reply, reply_markup=keyboard_markup)


@dp.message_handler(state=EditNote.Image, user_id=TG_ADMINS_ID, content_types=ContentType.VIDEO)
async def edit_note_image(message: Message, state: FSMContext):
    keyboard_markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Отмена', callback_data='cancel_admin')],
            [InlineKeyboardButton(text='Сохранить', callback_data='save_edit_note')],
        ]
    )
    await state.update_data(image=message.video.file_id)
    await EditNote.Confirm.set()
    data = await state.get_data()
    section = data.get('section')
    topic = data.get('topic')
    title = data.get('note_name')
    reply = f'Сохранить {section} в разделе {topic} под названием {title}?'
    await message.answer(text=reply, reply_markup=keyboard_markup)


@dp.callback_query_handler(state=EditNote.Confirm, text='save_edit_note', user_id=TG_ADMINS_ID)
async def mange_topic(call: CallbackQuery, state: FSMContext):
    await call.answer()
    data = await state.get_data()
    section = data.get('section')
    topic = data.get('topic')
    title = data.get('note_name')
    image = data.get('image')
    note_id = data.get('note')
    await state.finish()
    await Note.edit(note_id, section, topic, title, image)
    keyboard_markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Админ панель', callback_data='admin')],
            [InlineKeyboardButton(text='Управление',
                                  callback_data=manage_cb.new(section=section, action='mange'))],
            [InlineKeyboardButton(text='Добавить ещё',
                                  callback_data=manage_cb.new(section=section, action='add'))],
        ]
    )
    reply = f'Что дальше?'
    await call.message.answer(reply, reply_markup=keyboard_markup)
