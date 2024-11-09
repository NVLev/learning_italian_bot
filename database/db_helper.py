import os
import sys
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from db_config.db_config import settings

# from module_26_fastapi.homework.config.config import settings


class DatabaseHelper:
    """
    Tietokanta-avustaja, joka tarjoaa tietokantayhteyden ja istuntojen hallinnan.
    """

    def __init__(
        self,
        url: str,
        echo: bool = False,
        echo_pool: bool = True,
        pool_size: int = 5,  # количество соединий
        max_overflow: int = 10,
    ) -> None:
        """
        Alustaa tietokanta-avustajan.
        """
        self.engine: AsyncEngine = create_async_engine(
            url=url,
            echo=echo,
            echo_pool=echo_pool,
            pool_size=pool_size,
            max_overflow=max_overflow,
        )
        self.session_factory: async_sessionmaker[AsyncSession] = async_sessionmaker(
            bind=self.engine,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
        )

    async def dispose(self) -> None:
        """
        Sulkee tietokantayhteyden.
        """
        await self.engine.dispose()
        print("dispose engine")

    async def session_getter(self) -> AsyncGenerator[AsyncSession, None]:
        """
        Palauttaa uuden tietokanta-istunnon.

        :return: Asynkroninen istunto.
        """
        session = self.session_factory()
        async with session:
            yield session


db_helper = DatabaseHelper(
    url=settings.db.url,
    echo=settings.db.echo,
    echo_pool=settings.db.echo_pool,
    pool_size=settings.db.pool_size,
    max_overflow=settings.db.max_overflow,
)
