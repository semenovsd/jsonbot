import json
import logging

from gino import Gino
from gino.schema import GinoSchemaVisitor
from sqlalchemy import (BigInteger, Boolean, Column, String, sql, ARRAY, ForeignKey, Sequence, Integer, JSON)

from config import PG_HOST, POSTGRES_DB, POSTGRES_PASSWORD, POSTGRES_USER

db = Gino()


# Документация
# http://gino.fantix.pro/en/latest/tutorials/tutorial.html
class User(db.Model):
    __tablename__ = 'users'
    query: sql.Select

    tg_id = Column(BigInteger, unique=True, primary_key=True)
    tg_username = Column(String(32))
    tg_first_name = Column(String(32))
    tg_last_name = Column(String(32))
    poker_hosting = Column(String(3), default=None)
    id_club = Column(String(16), default=None)
    user_status = Column(Boolean(), default=False)

    @staticmethod
    async def get_or_create(tg_id):
        user = await User.query.where(User.tg_id == int(tg_id)).gino.first()
        if user:
            return user
        else:
            # args = message.get_args() if hasattr(message, 'get_args') else None
            # logging.info(args)
            # ?q=123456&w=ppp&e=1234567&r=nickname
            # ?q=123456&w=ppp&e=1234567&r=12345&t=nickname
            # q - id_пользователя
            # w - poker_hosting
            # e - id club
            # r - id пользователя в клубе
            new_user = User()
            new_user.tg_id = int(tg_id)
            await new_user.create()
            return new_user

    @staticmethod
    async def new_users():
        return await User.query.where(User.training_ready == False).gino.all()

    @staticmethod
    async def all_users():
        return [i[0] for i in await User.select('user_id').gino.all()]


async def create_db():
    await db.set_bind(f'postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{PG_HOST}/{POSTGRES_DB}')

    # Create tables
    db.gino: GinoSchemaVisitor
    await db.gino.drop_all()  # Drop the db
    await db.gino.create_all()
    # from onstart_load_db import onstart_loads  # Load DB start data
    # await onstart_loads()
