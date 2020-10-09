import logging

from gino import Gino
from gino.schema import GinoSchemaVisitor
from sqlalchemy import (BigInteger, Boolean, Column, String, sql)

from config import PG_HOST, POSTGRES_DB, POSTGRES_PASSWORD, POSTGRES_USER

db = Gino()


# Документация
# http://gino.fantix.pro/en/latest/tutorials/tutorial.html
class User(db.Model):
    __tablename__ = 'users'
    query: sql.Select

    tg_id = Column(BigInteger, unique=True, primary_key=True)
    tg_username = Column(String(64), default=None)
    tg_fullname = Column(String(64), default=None)
    site_user_id = Column(String(64), default=None)
    poker_hosting = Column(String(64), default=None)
    club_id = Column(String(64), default=None)
    club_user_id = Column(String(64), default=None)
    site_nickname = Column(String(64), default=None)
    is_registered = Column(Boolean(), default=False)

    @staticmethod
    async def get_or_create(message):
        user = await User.query.where(User.tg_id == int(message.from_user.id)).gino.first()
        if user:
            return user
        try:
            deep_link = message.get_args()
            site_user_id, poker_hosting, club_id, club_user_id, site_nickname = deep_link.split('|')
            new_user = User()
            new_user.user_id = int(message.from_user.id)
            new_user.username = str(message.from_user.username)
            new_user.full_name = str(message.from_user.full_name)
            new_user.site_user_id = str(site_user_id)
            new_user.poker_hosting = str(poker_hosting)
            new_user.club_id = str(club_id)
            new_user.club_user_id = str(club_user_id)
            new_user.site_nickname = str(site_nickname)
            await new_user.create()
            return new_user
        except Exception as e:
            logging.info(e, f'message \n\n\n\n ERROR !!!!!!!!!!!!!!!!!!')
            return None


async def create_db():
    await db.set_bind(f'postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{PG_HOST}/{POSTGRES_DB}')

    # Create tables
    db.gino: GinoSchemaVisitor
    await db.gino.drop_all()  # Drop the db
    await db.gino.create_all()
    # from onstart_load_db import onstart_loads  # Load DB start data
    # await onstart_loads()
