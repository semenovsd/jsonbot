from base64 import encode
from typing import Dict, Union

from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import CommandStart
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, Message, ContentType
from aiogram.utils.callback_data import CallbackData

from config import JSON_DATA_FILENAME
from database import User
from functions import read_json_data, get_method_data, service_unavailable, notification, photo_notification
from load_all import bot, dp

from states import AddProve

club_cb = CallbackData('deposit', 'club')
withdraw_cb = CallbackData('withdraw', 'action', 'club', 'method')


@dp.callback_query_handler(text='start')
@dp.message_handler(CommandStart())
async def start_cmd_handler(message: Union[Message, CallbackQuery], state: FSMContext, user: User):
    """
    Стартовый экран приветствия.
    :param message:
    :param state:
    :param user:
    :return:
    """
    await state.finish()
    deep_link = message.get_args() or None
    if deep_link:
        # Костыль. Из дб не отправить сообщения из за цикличиского испорта. Поэтому когда юзер заходит по диплинку,
        # то подразумевается, что он новый, поэтому отправляется сообщение здесь.
        msg = f'Registered user:\n' \
              f'tg_id: {user.tg_id}\n' \
              f'tg_username: {user.tg_username}\n' \
              f'tg_fullname: {user.tg_fullname}\n' \
              f'site_user_id: {user.site_user_id}\n' \
              f'poker_hosting: {user.poker_hosting}\n' \
              f'club_id: {user.club_id}\n' \
              f'club_user_id: {user.club_user_id}\n' \
              f'site_nickname: {user.site_nickname}\n'
        await notification(msg)

    keyboard_markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Show me The Clubs', callback_data='show_clubs')],
            [InlineKeyboardButton(text='Contacts', callback_data='contacts')]
        ]
    )
    await bot.send_sticker(message.from_user.id,
                           sticker='CAACAgIAAxkBAAIEkl-ASlxpJp73d5zjlQZ_jq8juS2EAAJnAQACufOXC1vlyNMSEWLrGwQ')
    reply = 'Hello! I can help you make withdraws or deposit! Press show clubs button.'
    await bot.send_message(message.from_user.id, text=reply, reply_markup=keyboard_markup)


@dp.callback_query_handler(text='contacts')
async def choice_method(call: CallbackQuery):
    """
    Экран контактов.
    :param call:
    :return:
    """
    await call.message.edit_reply_markup()

    keyboard_markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Back',
                                  callback_data='start')]
        ]
    )

    reply = 'For contact the admin write here @stspb'
    await call.message.answer_sticker(
        sticker='CAACAgIAAxkBAAIEll-AT82D6FdJbvup_NkjKrALBRTRAAIaAQACufOXC0nTPkIwChsqGwQ')
    await call.message.answer(text=reply, reply_markup=keyboard_markup)


@dp.callback_query_handler(text='show_clubs')
async def choice_method(call: CallbackQuery):
    """
    Стартовый экран при заходе в бота. Выводи список доступных клубов из джейсон файла.
    :param call:
    :return:
    """
    await call.message.edit_reply_markup()

    keyboard_markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Contacts', callback_data='contacts')]]
    )

    data = read_json_data(JSON_DATA_FILENAME)
    if data != 'File not read' and data.get('Clubs'):
        for club in data.get('Clubs'):
            keyboard_markup.add(
                InlineKeyboardButton(text=f'{club.get("Club_name")}',
                                     callback_data=club_cb.new(club=club.get('Club_name')))
            )
        reply = f'Choice the Club.'
        await call.message.answer(text=reply, reply_markup=keyboard_markup)
    else:
        await service_unavailable(call.from_user.id)


@dp.callback_query_handler(club_cb.filter())
async def choice_method(call: CallbackQuery, callback_data: Dict[str, str]):
    """
    Выводит по выбранному клубу список доступных методов пополнения из джейсон файла.
    ВАЖНО: Ограничение на суммарное название клуба, метода пополнения и названия действия 64 байта!
    :param call:
    :param callback_data:
    :return:
    """
    await call.message.edit_reply_markup()

    data = read_json_data(JSON_DATA_FILENAME)
    current_club = callback_data.get('club')

    if data != 'File not read' and data.get('Clubs'):

        keyboard_markup = InlineKeyboardMarkup()

        for club in data.get('Clubs'):
            if club.get('Club_name') == current_club:
                for _, value in club['Deposit'].items():
                    keyboard_markup.add(
                        InlineKeyboardButton(text=f'{value.get("Name")}',
                                             callback_data=withdraw_cb.new(action='view',
                                                                           club=club.get('Club_name'),
                                                                           method=value.get('Name')))
                    )

        keyboard_markup.add(
            InlineKeyboardButton(text='Contacts', callback_data='contacts'),
            InlineKeyboardButton(text='Back', callback_data='show_clubs'),
            InlineKeyboardButton(text='Withdraw',
                                 callback_data=withdraw_cb.new(action='withdraw', club=current_club, method='_'))
        )

        reply = f'Choice available method for {current_club}'
        await call.message.answer(reply, reply_markup=keyboard_markup)
    else:
        await service_unavailable(call.from_user.id)


@dp.callback_query_handler(withdraw_cb.filter(action='withdraw'))
async def deposit(call: CallbackQuery, callback_data: Dict[str, str], user: User):
    """
    Выводить кнопки пополнить и отправить скриншот пополнения.
    ВАЖНО: Ограничение на суммарное название клуба, метода пополнения и названия действия 64 байта!
    :param call:
    :param callback_data:
    :param user:
    :return:
    """
    await call.message.edit_reply_markup()
    club_name = callback_data.get('club')
    keyboard_markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Show me the Clubs', callback_data='show_clubs')],
            [InlineKeyboardButton(text='Contacts', callback_data='contacts')]
        ]
    )

    msg = f'Пользоатель ID {user.tg_id} (@{user.tg_username}) запросил вывод для клуба {club_name}'
    send = await notification(msg)
    if send:
        reply = f'Your request has been sent to the administrator!'
        await call.message.answer(reply, reply_markup=keyboard_markup)
    else:
        await service_unavailable(call.from_user.id)


@dp.callback_query_handler(withdraw_cb.filter(action='view'))
async def deposit(call: CallbackQuery, callback_data: Dict[str, str]):
    """
    Выводить кнопки пополнить и отправить скриншот пополнения.
    ВАЖНО: Ограничение на суммарное название клуба, метода пополнения и названия действия 64 байта!
    :param call:
    :param callback_data:
    :return:
    """
    await call.message.edit_reply_markup()
    club_name = callback_data.get('club')
    method_name = callback_data.get('method')
    method = get_method_data(club_name, method_name, JSON_DATA_FILENAME)
    keyboard_markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Back', callback_data=club_cb.new(club=club_name))],
            [InlineKeyboardButton(text='Deposit',
                                  callback_data=withdraw_cb.new(action='transfer',
                                                                club=club_name,
                                                                method=method_name))],
            [InlineKeyboardButton(text='Send screenshot prove',
                                  callback_data=withdraw_cb.new(action='prove',
                                                                club=club_name,
                                                                method=method_name))],
        ]
    )
    reply = f'{method.get("Name")} for {club_name}:\n' \
            f'Account bill: {method.get("Account_bill")}\n' \
            f'Country bill: {method.get("Country_bill")}\n' \
            f'Name_owner: {method.get("Andrey")}\n' \
            f'Commet to pay: {method.get("Commet_topay")}\n' \
            f'Fee: {method.get("Fee")} %\n' \
            f'Additional info: {method.get("Additinal_comment")}'
    # await call.message.answer_photo(photo=f'{method.get("Url_icon")}', caption=reply, reply_markup=keyboard_markup)
    await call.message.answer(reply, reply_markup=keyboard_markup)


@dp.callback_query_handler(withdraw_cb.filter(action='transfer'))
async def deposit(call: CallbackQuery, callback_data: Dict[str, str], user: User):
    """
    Хэндлер отправляет уведомление (сообщение) в чат о желании пользователя пополнить выбранным методом данный клуб.
    Также добавлять пользователю лог об отправке данного сообщения, для блокировки повторной отправки уведомления.
    ВАЖНО: Ограничение на суммарное название клуба, метода пополнения и названия действия 64 байта!
    :param call:
    :param callback_data:
    :param user:
    :return:
    """
    await call.message.edit_reply_markup()
    club_name = callback_data.get('club')
    method = callback_data.get('method')
    keyboard_markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Back', callback_data=withdraw_cb.new(action='view',
                                                                             club=club_name,
                                                                             method=method))],
        ]
    )
    msg = f'Пользователь ID {user.tg_id} (@{user.tg_username}) хочет пополнить методом {method} для клуба {club_name}'
    send = await notification(msg)
    if send:
        reply = f'Заявка получена  Клуб ID : 00000  ID игрока: 00000 Покер Хостинг: xxx'
        await call.message.answer(reply, reply_markup=keyboard_markup)
    else:
        await service_unavailable(call.from_user.id)


@dp.callback_query_handler(withdraw_cb.filter(action='prove'))
async def ask_photo_prove(call: CallbackQuery, callback_data: Dict[str, str], state: FSMContext):
    """
    Хэндлер для отправки скриншота пополнения. Пользователя просят отправить скриншот (тип фала - фото).
    Можно только отменить и выйти в главное меню или отправить фото.
    ВАЖНО: Ограничение на суммарное название клуба, метода пополнения и названия действия 64 байта!
    :param call:
    :return:
    """
    await call.message.edit_reply_markup()

    await AddProve.Image.set()
    club_name = callback_data.get('club')
    method = callback_data.get('method')
    await state.update_data(club_name=club_name, method=method)
    keyboard_markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Cancel', callback_data='cancel')]
        ]
    )

    reply = f'Send me photo prove payment.'
    await call.message.answer(reply, reply_markup=keyboard_markup)


@dp.message_handler(state=AddProve.Image, content_types=ContentType.PHOTO)
async def get_photo_prove(message: Message, state: FSMContext, user: User):
    """
    Хэндлер получает от пользователя фото и отправляет информацию в чат оповещения.
    ВАЖНО: Ограничение на суммарное название клуба, метода пополнения и названия действия 64 байта!
    :param message:
    :param state:
    :return:
    """
    data = await state.get_data()
    club_name = data.get('club_name')
    method_name = data.get('method')
    photo = message.photo[0].file_id
    await state.finish()
    keyboard_markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Cancel',
                                  callback_data=withdraw_cb.new(action='transfer',
                                                                club=club_name,
                                                                method=method_name))]
        ]
    )
    msg = f'Подтверждение от пользователя ID {user.tg_id} (@{user.tg_username}) о пополнение ' \
          f'методом {method_name} для клуба {club_name}'
    send = await photo_notification(msg, photo)
    if send:
        reply = f'Great! The prove has been send! Wait for the answer soon!'
        await message.answer(reply, reply_markup=keyboard_markup)
    else:
        await service_unavailable(message.from_user.id)


@dp.message_handler(state=AddProve.Image)
async def no_photo_prove(message: Message):
    """
    Предлагает пользователю повторно отправить сообщение или нажать отмена.
    ВАЖНО: Ограничение на суммарное название клуба, метода пополнения и названия действия 64 байта!
    :param message:
    :return:
    """

    keyboard_markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Отмена', callback_data='cancel')]
        ]
    )

    reply = f'Sorry, i can get only photo. Send me photo file!'
    await message.answer(reply, reply_markup=keyboard_markup)
