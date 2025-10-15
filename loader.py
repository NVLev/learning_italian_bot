from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from db_config.db_config import settings  # ИСПРАВЛЕНО: новый импорт

bot = Bot(
    token=settings.bot.token,  # ИСПРАВЛЕНО: используем settings
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

# все данные бота, которые мы не сохраняем в БД
# (к примеру состояния), будут стёрты при перезапуске
dp = Dispatcher(storage=MemoryStorage())