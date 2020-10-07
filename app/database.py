import json

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

    user_id = Column(BigInteger, unique=True, primary_key=True)
    name = Column(String(50), default=None)
    gender = Column(String(5), default=None)
    age = Column(String(2), default=None)
    height = Column(String(3), default=None)
    weight = Column(String(3), default=None)
    goal = Column(String(50), default=None)
    lifestyle = Column(String(50), default=None)
    place = Column(String(50), default=None)
    home_stuff = Column(String(50), default=None)
    phone_number = Column(String(12), default=None)
    email = Column(String(30), default=None)
    registered = Column(Boolean(), default=False)
    training_ready = Column(Boolean(), default=False)
    is_trainer = Column(Boolean(), default=False)

    @staticmethod
    async def get_or_create(user_id):
        user = await User.query.where(User.user_id == int(user_id)).gino.first()
        if user:
            return user
        else:
            new_user = User()
            new_user.user_id = int(user_id)
            await new_user.create()
            return new_user

    @staticmethod
    async def new_users():
        return await User.query.where(User.training_ready == False).gino.all()

    @staticmethod
    async def all_users():
        return [i[0] for i in await User.select('user_id').gino.all()]


class Section(db.Model):
    __tablename__ = 'sections'
    query: sql.Select

    name = Column(String(64), unique=True, primary_key=True)
    topics = Column(ARRAY(String(256)), default=list())

    @staticmethod
    async def get(name):
        return await Section.query.where(Section.name == name).gino.first()

    @staticmethod
    async def get_all_names():
        return [i[0] for i in await Section.select('name').gino.all()]


class Note(db.Model):
    __tablename__ = 'notes'
    query: sql.Select

    id = Column(Integer, Sequence('notes_id_seq'), primary_key=True, unique=True)
    section = Column(String(64), ForeignKey('sections.name'))
    topic = Column(String(256))
    title = Column(String(128), default=None)
    image = Column(String(128), default=None)

    @staticmethod
    async def get(id):
        return await Note.query.where(Note.id == int(id)).gino.first()

    @staticmethod
    async def add(section, topic, title, image):
        new_note = Note()
        new_note.section = section
        new_note.topic = topic
        new_note.title = title
        new_note.image = image
        await new_note.create()
        return new_note

    @staticmethod
    async def edit(note_id, section, topic, title, image):
        note = await Note.get(note_id)
        await note.update(
            section=section,
            topic=topic,
            title=title,
            image=image
        ).apply()

    @staticmethod
    async def get_all(section, topic):
        return await Note.query.where((Note.section == section) & (Note.topic == topic)).gino.all()


# db.select([db.func.count()]).where(
#            (User.referrer == self.user_id) & (User.subscribe == True)).gino.scalar()
# nutrition
# pharma
# medical


class Trainer(db.Model):
    pass


class Token(db.Model):
    pass


class TrainingPlan(db.Model):
    __tablename__ = 'plans'
    query: sql.Select

    name = Column(String(64), primary_key=True)
    gender = Column(String(5), default=None)
    goal = Column(String(50), default=None)
    lifestyle = Column(String(50), default=None)
    place = Column(String(50), default=None)
    description = Column(String(1024), default=None)
    author = Column(BigInteger())
    monday = Column(JSON(2048))
    tuesday = Column(JSON(2048))
    wednesday = Column(JSON(2048))
    thursday = Column(JSON(2048))
    friday = Column(JSON(2048))
    saturday = Column(JSON(2048))
    sunday = Column(JSON(2048))

    @staticmethod
    async def get_plan(name):
        return await TrainingPlan.query.where(TrainingPlan.name == name).gino.first()

    @staticmethod
    async def add(data):
        plan = TrainingPlan()
        plan.name = data.get('name')
        plan.gender = data.get('gender')
        plan.goal = data.get('goal')
        plan.lifestyle = data.get('lifestyle')
        plan.place = data.get('place')
        plan.home_stuff = data.get('home_stuff')
        plan.description = data.get('description')
        plan.author = data.get('author')
        await plan.create()

    async def view_day(self, day_name):
        return json.loads(self.__dict__['__values__'].get(day_name)) if self.__dict__['__values__'].get(
            day_name) else None

    @staticmethod
    async def add_task(data):
        plan = await TrainingPlan.get_plan(data.get('plan_name'))
        task = {data.get('task_time'): {'name': data.get('task_name'),
                                        'time': data.get('task_time'),
                                        'section': data.get('section_name'),
                                        'author': data.get('task_author'),
                                        'tasks': []}
                }
        day_name = data.get('day_name')
        day = plan.view_day(day_name)
        day.update(task)
        await plan.update(
            **{day_name: json.dumps(day)}
        ).apply()

    @staticmethod
    async def get_all_names():
        return [i[0] for i in await TrainingPlan.select('name').gino.all()]


async def create_db():
    await db.set_bind(f'postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{PG_HOST}/{POSTGRES_DB}')

    # Create tables
    db.gino: GinoSchemaVisitor
    await db.gino.drop_all()  # Drop the db
    await db.gino.create_all()
    from onstart_load_db import onstart_loads  # Load DB start data
    await onstart_loads()
