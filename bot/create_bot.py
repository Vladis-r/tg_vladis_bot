from aiogram import Bot, Dispatcher
import os

from aiogram.contrib.fsm_storage.memory import MemoryStorage
from dotenv import load_dotenv

load_dotenv()

bot = Bot(token=os.environ.get("TG_TOKEN"))
dp = Dispatcher(bot, storage=MemoryStorage())
