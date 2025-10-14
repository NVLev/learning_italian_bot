from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from db_config.db_config import settings

class DatabaseHelper:
    def __init__(self):
        self.engine = create_async_engine(
            url=settings.db.url.unicode_string(), # Используем настройки отсюда
            echo=settings.db.echo,
            pool_size=settings.db.pool_size,
            max_overflow=settings.db.max_overflow,
        )
        self.session_factory = async_sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
            autocommit=False
        )

    @asynccontextmanager
    async def get_session(self) -> AsyncSession:
        session = self.session_factory()
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            raise e
        finally:
            await session.close()


db_helper = DatabaseHelper()

