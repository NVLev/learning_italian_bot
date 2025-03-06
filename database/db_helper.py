from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession
from config_data.config import db_config

class DatabaseHelper:
    @staticmethod
    @asynccontextmanager
    async def get_session() -> AsyncSession:
        session = db_config.async_session()
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            raise e
        finally:
            await session.close()

db_helper = DatabaseHelper()

# import os
# import sys
# from typing import AsyncGenerator
# from contextlib import asynccontextmanager
# from sqlalchemy.ext.asyncio import (
#     AsyncEngine,
#     AsyncSession,
#     async_sessionmaker,
#     create_async_engine,
# )
#
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# from db_config.db_config import settings
#
# # from module_26_fastapi.homework.config.config import settings
#
#
# class DatabaseHelper:
#     """
#     Хелпер обеспечивает подключение к базам данных и управление сеансами.
#     """
#
#     def __init__(self, url: str, **kwargs):
#         self.engine = create_async_engine(
#             url=url,
#             pool_pre_ping=True,  # для проверки соединения
#             **kwargs
#         )
#         self.session_factory = async_sessionmaker(
#             bind=self.engine,
#             class_=AsyncSession,
#             expire_on_commit=False,
#             autoflush=False,
#             autocommit=False
#         )
#
#     @asynccontextmanager
#     async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
#         async with self.session_factory() as session:
#             try:
#                 yield session
#             except Exception as e:
#                 await session.rollback()
#                 raise e
#             finally:
#                 await session.close()
#
#
# db_helper = DatabaseHelper(
#     url=settings.db.url,
#     echo=settings.db.echo,
#     echo_pool=settings.db.echo_pool,
#     pool_size=settings.db.pool_size,
#     max_overflow=settings.db.max_overflow,
# )
