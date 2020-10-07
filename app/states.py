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


class AddTopic(StatesGroup):
    Name = State()
    Image = State()
    Confirm = State()


class EditNote(StatesGroup):
    Name = State()
    Image = State()
    Confirm = State()


class AddPlan(StatesGroup):
    Name = State()
    Gender = State()
    Goal = State()
    Lifestyle = State()
    Place = State()
    HomeStuff = State()
    Description = State()
    Confirm = State()


class PlanDetails(StatesGroup):
    ChoiceDay = State()
    AddTask = State()
    AddTaskName = State()
    AddTaskTime = State()
    ConfirmAddTask = State()
    ChoiceTopic = State()


class Mailing(StatesGroup):
    Receiver = State()
    Text = State()
    Language = State()


class Support(StatesGroup):
    Message = State()
