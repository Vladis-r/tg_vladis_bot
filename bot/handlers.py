import os
from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import StatesGroup, State

from bot.keyboards import get_image_keyboard, get_main_keyboard, get_cancel_keyboard, get_pool_keyboard
from bot.create_bot import bot
from bot.utils import get_image, get_weather, get_exchange_rate


class MenuState(StatesGroup):
    main_state = State()
    weather_state = State()
    currency_state = State()
    image_state = State()
    poll_question_state = State()
    poll_options_state = State()
    poll_check = State()


async def start(message: types.Message):
    """
    Хендлер команды /start.
    Приветствие.
    """
    await MenuState.main_state.set()
    await message.answer("Добро пожаловать!", reply_markup=get_main_keyboard())


async def cancel_handler(message: types.Message, state: FSMContext):
    """
    Хендлер команды /cancel.
    Возвращение в главное меню.
    """
    await MenuState.main_state.set()
    await message.reply("Вы вернулись в главное меню", reply_markup=get_main_keyboard())


async def return_handler(message: types.Message, state: FSMContext):
    await MenuState.previous()
    await message.reply("Попробуйте ещё раз")


async def main_menu(message: types.Message, state: FSMContext):
    """
    Хендлер выбора функции
    """
    if message.text == "Погоду":
        await message.answer("Напишите имя города:", reply_markup=get_cancel_keyboard())
        await MenuState.weather_state.set()
    elif message.text == "Курс валюты":
        await message.answer("Введите значения для конвертации в формате: 10 usd rub",
                             reply_markup=get_cancel_keyboard())
        await MenuState.currency_state.set()

    elif message.text == "Создать опрос":
        await message.answer("Напишите свой вопрос.", reply_markup=get_cancel_keyboard())
        await MenuState.poll_question_state.set()

    elif message.text == "Картинку" or message.text == "Давай ещё!":
        await image_menu(message)

    else:
        await message.reply("Нажми на кнопку, получишь результат и твоя мечта осуществится...")


async def weather_menu(message: types.Message, state: FSMContext):
    """
    Хендлер погоды.
    Возвращает текст с прогнозом погоды на момент отправки.
    """
    city = message.text
    weather = await get_weather(city)
    if weather is None:
        await message.answer("Неправильно назван город.", reply_markup=get_cancel_keyboard())
    else:
        await message.reply(weather, reply_markup=get_main_keyboard())
        await MenuState.main_state.set()


async def currency_menu(message: types.Message, state: FSMContext):
    """
    Хендлер конвертации валюты.
    Возвращает реузльтат конвертации и курс на момент отправки.
    """
    data = message.text.split()
    if len(data) == 3:
        amount, cur_from, cur_to = data
        rate = await get_exchange_rate(amount, cur_from, cur_to)
        await message.reply(rate, reply_markup=get_main_keyboard())
        await MenuState.main_state.set()
    else:
        await message.reply("Введите 3 значения через пробел в формате: 10 usd rub")


async def pool_question_menu(message: types.Message, state: FSMContext):
    """
    Хендлер опроса.
    Записывает вопрос в память и предлагает написать варианты ответа.
    """
    async with state.proxy() as data:
        data["question"] = message.text
    await message.reply("Теперь предложите варианты ответов через запятую.", reply_markup=get_pool_keyboard())
    await MenuState.poll_options_state.set()


async def pool_options_menu(message: types.Message, state: FSMContext):
    """
    Хендлер опроса 2.
    Записывает варианты ответа в память,
    запрашивает подтверждение отправки опроса в группу.
    """
    options = [opt.strip() for opt in message.text.split(",")]
    async with state.proxy() as data:
        data["options"] = options
        question = data["question"]

    options = ", ".join(options)
    await message.answer(f"Отправить опрос? Ваш вопрос:\n{question}\nВарианты ответов:\n{options}",
                         reply_markup=get_pool_keyboard())
    await MenuState.poll_check.set()


async def pool_check_handler(message: types.Message, state: FSMContext):
    """
    Хендлер опроса 3.
    Принимает подтверждающий ответ
    """
    agree_message = ["Да", "Верно", "Точно", "Конечно", "Угу", "Именно", "Правильно", "Ага", "Несомненно", "Однозначно",
                     "Yes", "Yeah", "Yea", "Affirmative", "Absolutely", "Certainly", "Sure", "Definitely",
                     "Roger", "Aye", "Yup", "Right", "Ok", "Of course", "Yep", "Da"]

    disagree_message = ["No", "Нет", "Nope", "Никак нет", "Nix", "Negative", "Отрицательно", "Never", "Никогда", "Net",
                        "Не надо", "Ne nado", "Ne", "Не"]

    if message.text.capitalize() in disagree_message:
        await message.answer("Вы отменили опрос. Вы можете изменить его или перейти в главное меню")

    elif message.text.capitalize() in agree_message:
        chat_id = os.getenv("GROUP_CHAT_ID")
        async with state.proxy() as data:
            question = data["question"]
            options = data["options"]
        await bot.send_poll(chat_id=chat_id, question=question, options=options)
        await message.answer("Опрос создан", reply_markup=get_main_keyboard())
        await MenuState.main_state.set()
    else:
        await message.reply("Я вас не понял. Отправить опрос?")


async def image_menu(message: types.Message):
    """
    Функция отправки картинки
    """
    await message.answer(f"Немного подождём...", reply_markup=get_image_keyboard())
    url_image = await get_image()
    if url_image:
        image = types.InputFile.from_url(url=url_image, filename="filename")
        await bot.send_photo(photo=image, chat_id=message.chat.id)
    else:
        await message.answer("Что-то пошло не так")


def register_handlers(dp: Dispatcher):
    dp.register_message_handler(start, commands=["start"], state=None)
    dp.register_message_handler(start, content_types=types.ContentTypes.TEXT, state=None)
    dp.register_message_handler(cancel_handler, commands=["cancel"], state="*")
    dp.register_message_handler(cancel_handler, Text(equals="Главное меню", ignore_case=True), state="*")
    dp.register_message_handler(return_handler, Text(equals="Вернуться", ignore_case=True),
                                state=[MenuState.poll_options_state, MenuState.poll_check])
    dp.register_message_handler(main_menu, state=MenuState.main_state)
    dp.register_message_handler(weather_menu, state=MenuState.weather_state)
    dp.register_message_handler(currency_menu, state=MenuState.currency_state)
    dp.register_message_handler(pool_question_menu, state=MenuState.poll_question_state)
    dp.register_message_handler(pool_options_menu, state=MenuState.poll_options_state)
    dp.register_message_handler(pool_check_handler, state=MenuState.poll_check)
