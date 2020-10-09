# add send broadcast. Add get data
import json
import logging
from asyncio import sleep

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import exceptions

from load_all import bot


async def send_messages(message: str, users_id: list):
    log = logging.getLogger('broadcast')
    for user_id in users_id:
        try:
            await bot.send_message(user_id, message)
            await sleep(0.05)  # Telegram limit 30 message per second, here set 20 msg per second
        except exceptions.BotBlocked:
            log.error(f"Target [ID:{user_id}]: blocked by user")
        except exceptions.ChatNotFound:
            log.error(f"Target [ID:{user_id}]: invalid user ID")
        except exceptions.RetryAfter as e:
            log.error(f"Target [ID:{user_id}]: Flood limit is exceeded. Sleep {e.timeout} seconds.")
            await sleep(e.timeout)
            return await send_messages(message, user_id)
        except exceptions.UserDeactivated:
            log.error(f"Target [ID:{user_id}]: user is deactivated")
        except exceptions.TelegramAPIError:
            log.exception(f"Target [ID:{user_id}]: failed")
            pass
        else:
            log.info(f"Target [ID:{user_id}]: success")


def read_json_data(file_name):
    try:
        with open(file_name, 'r', encoding='utf-8') as f:
            text = json.load(f)
        return text
    except OSError:
        return 'File not read'


def get_method_data(club_name, method_name, file_name):
    data = read_json_data(file_name)
    if data != 'File not read' and data.get('Clubs'):
        for club in data.get('Clubs'):
            if club.get('Club_name') == club_name:
                for _, value in club['Deposit'].items():
                    if value.get("Name") == method_name:
                        return value


async def service_unavailable(chat_id):
    keyboard_markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Contacts', callback_data='contacts')]]
    )
    reply = 'The service is temporarily unavailable, please try again later'
    await bot.send_sticker(chat_id,
                           sticker='CAACAgIAAxkBAAIElF-ATNnW9y3WVWgDjLxOC5yvhY5QAAIUAQACufOXC5ZJByYQOH2bGwQ')
    await bot.send_message(chat_id, text=reply, reply_markup=keyboard_markup)






