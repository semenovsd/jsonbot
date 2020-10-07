from database import Section, TrainingPlan


async def onstart_loads():
    workout = Section()
    workout.name = 'workout'
    workout.topics = ['Грудь', 'Спина', 'Ноги', 'Ягодичные', 'Дельты', 'Руки Бицепс', 'Руки Трицепс', 'Предплечье',]
                      # 'Пресс', 'Функциональные упражнения', 'Кардио', 'Растяжка']
    await workout.create()

    nutrition = Section()
    nutrition.name = 'nutrition'
    nutrition.topics = ['Завтрак', 'Ланч', 'Обед', 'Ужин']
    await nutrition.create()

    pharma = Section()
    pharma.name = 'pharma'
    pharma.topics = ['BCA', 'Protein', 'L-Carnitin', 'Creatin']
    await pharma.create()

    medical = Section()
    medical.name = 'medical'
    medical.topics = ['Кровь', 'Общие анализы', 'Гормоны']
    await medical.create()

    plan = TrainingPlan()
    plan.name = 'Программа для похудения'
    plan.gender = 'woman'
    plan.goal = 'lose_fat'
    plan.lifestyle = 'active'
    plan.place = 'workout_training'
    plan.home_stuff = 'None'
    plan.description = 'Программа для девочек ведущих активный образ жизни и занимающихся в зале'
    plan.author = 395415524
    await plan.create()
