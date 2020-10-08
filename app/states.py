from aiogram.dispatcher.filters.state import State, StatesGroup


class Newbie(StatesGroup):
    Name = State()
    Gender = State()
    Age = State()
    Height = State()
    Weight = State()
    Goal = State()
    Lifestyle = State()
    Place = State()
    HomeStuff = State()
    PhoneNumber = State()
    Email = State()
    Confirm = State()


class AddProve(StatesGroup):
    Image = State()


class Mailing(StatesGroup):
    Receiver = State()
    Text = State()
    Language = State()


class Support(StatesGroup):
    Message = State()
