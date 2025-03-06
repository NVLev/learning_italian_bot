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


class DatabaseConfig:
    def __init__(self):
        self.URL = os.getenv("CONFIG__DB__URL")
        self.ECHO = os.getenv("DB_ECHO", "False").lower() == "true"
        self.POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "10"))

        self.engine = create_async_engine(
            self.URL,
            echo=self.ECHO,
            pool_size=self.POOL_SIZE
        )
        self.async_session = sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )


db_config = DatabaseConfig()
BOT_TOKEN = os.getenv("BOT_TOKEN")
# BOT_TOKEN = os.getenv("BOT_TOKEN")
# DB_PATH = ''
# DATABASE_URL = os.getenv("CONFIG__DB__URL")
# engine = create_async_engine(
#                 DATABASE_URL,
#                 echo=True,
# )
# async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
#
#
#
#
# API_BASE_URL = ""