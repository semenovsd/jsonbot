from typing import Dict, Union

from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import CommandStart
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, Message, ContentType
from aiogram.utils.callback_data import CallbackData

from config import JSON_DATA_FILENAME
from functions import read_json_data
from load_all import bot, dp

from states import AddProve

deposit_cb = CallbackData('deposit', 'club')
withdraw_cb = CallbackData('withdraw', 'action', 'club', 'method')


@dp.callback_query_handler(text='start')
@dp.message_handler(CommandStart())
async def start_cmd_handler(message: Union[Message, CallbackQuery]):
    '''
    Стартовый экран при заходе в бота. Выводи список доступных клубов из джейсон файла.
    :param message:
    :return:
    '''
    # args = message.get_args() if hasattr(message, 'get_args') else None
    # зарегистрировать пользователя с данными из диплинка

    data = read_json_data(JSON_DATA_FILENAME)
    if data != 'File not read' and data.get('Clubs'):
        for club in data.get('Clubs'):
            keyboard_markup = InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text='Пополнить',
                                          callback_data=deposit_cb.new(club=club.get('Club_name')))]]
            )
            reply = f'Пополнить для клуба {club.get("Club_name")}'
            await bot.send_message(message.from_user.id, reply=reply, reply_markup=keyboard_markup)
    else:
        keyboard_markup = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text='Контакты для связи', callback_data='contacts')]]
        )
        reply = 'В данный момент сервис не доступен, попробуйте позднее.'
        await bot.send_message(message.from_user.id, reply=reply, reply_markup=keyboard_markup)


@dp.callback_query_handler(deposit_cb.filter())
async def choice_method(call: CallbackQuery, callback_data: Dict[str, str]):
    """
    Выводит по выбранному клубу список доступных методов пополнения из джейсон файла.
    ВАЖНО: Ограничение на суммарное название клуба, метода пополнения и названия действия 64 байта!
    :param call:
    :param callback_data:
    :return:
    """
    await call.answer()
    await call.message.edit_reply_markup()
    keyboard_markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Назад',
                                  callback_data='start')]]
    )
    # в следующем окне отправляем уведомление в чат.
    data = read_json_data(JSON_DATA_FILENAME)
    current_club = callback_data.get('club')
    if data != 'File not read' and data.get('Clubs'):
        for club in data.get('Clubs'):
            if club.get('Club_name') == current_club:
                for method in club.get('Deposit'):
                    keyboard_markup.add(
                        InlineKeyboardButton(text=f'{method.get("Name")}',
                                             callback_data=withdraw_cb.new(action='view',
                                                                           club=club.get('Club_name'),
                                                                           method=method.get('Name'))),
                    )

    reply = f'Варианты пополнения для клуба {current_club}'
    await call.message.answer(reply, reply_markup=keyboard_markup)


@dp.callback_query_handler(withdraw_cb.filter(action='view'))
async def deposit(call: CallbackQuery, callback_data: Dict[str, str]):
    """
    Выводить кнопки пополнить и отправить скриншот пополнения.
    ВАЖНО: Ограничение на суммарное название клуба, метода пополнения и названия действия 64 байта!
    :param call:
    :param callback_data:
    :return:
    """
    await call.answer()
    await call.message.edit_reply_markup()
    current_club = callback_data.get('club')
    method = callback_data.get('method')
    keyboard_markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Назад', callback_data=deposit_cb.new(club=current_club))],
            [InlineKeyboardButton(text='Пополнить',
                                  callback_data=withdraw_cb.new(action='transfer',
                                                                club=current_club,
                                                                method=method))],
            [InlineKeyboardButton(text='Отправить скриншот пополнения',
                                  callback_data=withdraw_cb.new(action='prove',
                                                                club=current_club,
                                                                method=method))],
        ]

    )

    reply = f'Пополненить клуб {current_club} через {method} (КАКУЮ ЕЩЁ ИНФУ ВЫВЕСТИ????)'
    await call.message.answer(reply, reply_markup=keyboard_markup)


@dp.callback_query_handler(withdraw_cb.filter(action='transfer'))
async def deposit(call: CallbackQuery, callback_data: Dict[str, str]):
    """
    Хэндлер отправляет уведомление (сообщение) в чат о желании пользователя пополнить выбранным методом данный клуб.
    Также добавлять пользователю лог об отправке данного сообщения, для блокировки повторной отправки уведомления.
    ВАЖНО: Ограничение на суммарное название клуба, метода пополнения и названия действия 64 байта!
    :param call:
    :param callback_data:
    :return:
    """
    # TODO make send notification
    await call.answer()
    await call.message.edit_reply_markup()
    current_club = callback_data.get('club')
    method = callback_data.get('method')
    keyboard_markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Назад', callback_data=withdraw_cb.new(action='view',
                                                                              club=current_club,
                                                                              method=method))],
        ]
    )

    reply = f'Заявка получена и с тобой свяжутся в ближайшее время! (КАКУЮ ЕЩЁ ИНФУ ВЫВЕСТИ????)'
    await call.message.answer(reply, reply_markup=keyboard_markup)


@dp.callback_query_handler(withdraw_cb.filter(action='prove'))
async def ask_photo_prove(call: CallbackQuery, state: FSMContext):
    """
    Хэндлер для отправки скриншота пополнения. Пользователя просят отправить скриншот (тип фала - фото).
    Можно только отменить и выйти в главное меню или отправить фото.
    ВАЖНО: Ограничение на суммарное название клуба, метода пополнения и названия действия 64 байта!
    :param state:
    :param call:
    :return:
    """
    # TODO make sand photo prove
    await call.answer()

    await AddProve.Image.set()
    data = await state.get_data()
    keyboard_markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Отмена', callback_data='')]  # TODO cancel
        ]
    )

    reply = f'Отправь мне скриншот подтверждение перевода.'
    await call.message.answer(reply, reply_markup=keyboard_markup)


@dp.message_handler(state=AddProve.Image, content_types=ContentType.PHOTO)
async def get_photo_prove(message: Message, state: FSMContext):
    """
    Хэндлер получает от пользователя фото и отправляет информацию в чат оповещения.
    ВАЖНО: Ограничение на суммарное название клуба, метода пополнения и названия действия 64 байта!
    :param message:
    :param state:
    :return:
    """
    data = await state.get_data()
    await state.finish()

    keyboard_markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='К ... (куда его отсюда вести?)', callback_data='')]  # TODO
        ]
    )

    reply = f'Отлично! Фото получено! Ожидай подтверждения в ближайшее время! Данные по фото {message.photo[0]}'
    await message.answer(reply, reply_markup=keyboard_markup)


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
            [InlineKeyboardButton(text='Отмена', callback_data='')]  # TODO cancel
        ]
    )

    reply = f'Я принимаю только ФОТО. Отправь фото или нажми отменя для возврата в предыдущее меню.'
    await message.answer(reply, reply_markup=keyboard_markup)

