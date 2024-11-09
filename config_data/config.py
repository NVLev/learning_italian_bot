import os

import logging
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from dotenv import load_dotenv, find_dotenv

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


if not find_dotenv():
    exit("Переменные окружения не загружены т.к отсутствует файл .env")
else:
    load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
DB_PATH = ''
DATABASE_URL = os.getenv("CONFIG__DB__URL")
engine = create_async_engine(
                DATABASE_URL,
                echo=True,
)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)




API_BASE_URL = ""