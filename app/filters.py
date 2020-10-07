from aiogram.dispatcher.handler import ctx_data

from database import User


def is_new_user(handlers) -> bool:
    data = ctx_data.get()
    user: User = data['user']
    return False if user.registered else True


def is_reg_user(handlers) -> bool:
    data = ctx_data.get()
    user: User = data['user']
    return user.registered


# def subscription_is_over(handlers) -> bool:
#     data = ctx_data.get()
#     user: User = data['user']
#     try:
#         return True if user.subscribe and user.subscribe_end_date < datetime.now() else False
#     except (AttributeError, TypeError, ValueError):
#         return False
#     # return True if hasattr(user, 'subscribe') and user.subscribe is True else False
