from aiogram import types
from aiogram.types import KeyboardButton


def get_main_keyboard():
    """
    Клавиатура main
    """
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    bt_1 = KeyboardButton("Погоду")
    bt_2 = KeyboardButton("Курс валюты")
    bt_3 = KeyboardButton("Создать опрос")
    bt_4 = KeyboardButton("Картинку")
    keyboard.row(bt_1, bt_2, bt_3, bt_4)
    return keyboard


def get_cancel_keyboard():
    """
    Клавиатура для /cancel
    """
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    keyboard.add(types.KeyboardButton("Главное меню"))
    return keyboard


def get_image_keyboard():
    """
    Клавиатура для картинки
    """
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    keyboard.add(types.KeyboardButton("Давай ещё!"))
    keyboard.add(types.KeyboardButton("Главное меню"))
    return keyboard


def get_pool_keyboard():
    """
    Клавиатура для опроса
    """
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    kb_1 = KeyboardButton("Вернуться")
    kb_2 = KeyboardButton("Главное меню")
    keyboard.row(kb_1, kb_2)
    return keyboard
