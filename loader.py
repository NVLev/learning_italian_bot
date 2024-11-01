from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from config_data.config import BOT_TOKEN

bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML) # используем html разметку
# все данные бота, которые мы не сохраняем в БД
# (к примеру состояния), будут стёрты при перезапуске
dp = Dispatcher(storage=MemoryStorage())
