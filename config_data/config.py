import os

import logging


from dotenv import load_dotenv, find_dotenv

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


if not find_dotenv():
    exit("Переменные окружения не загружены т.к отсутствует файл .env")
else:
    load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
DB_PATH = 'chat_database.db'


DEFAULT_COMMANDS = (
    ("start", "🚀 Запуск бота"),
    ("help", "\U0001F4A1 Обзор команд"),
    ("", ""),
    ('', ''),
    ('', ''),
    ('', '')
    # из состояний - кастомные команды
)
API_BASE_URL = ""