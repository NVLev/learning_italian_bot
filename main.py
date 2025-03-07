import asyncio

from aiogram.filters import Command

from admin.handlers import router
from loader import bot, dp
from admin.start_handlers import start_router
from admin.quiz_handlers import quiz_router
from config_data.config import logger, db_config
from utils.set_commands import set_commands
from middleware.middleware import DatabaseMiddleware
from model.model import Base  # Импорт моделей
from database.db_main import start_import


async def create_tables():
    """Создание таблиц в БД при старте приложения"""
    async with db_config.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Таблицы БД успешно созданы")



async def main():
    try:
        await create_tables()

        await start_import()
        logger.info("Данные успешно импортированы")

        dp.update.middleware(DatabaseMiddleware())
        logger.info('middleware passed')
        # подключает к диспетчеру все обработчики, которые используют router
        dp.include_router(start_router)
        dp.include_router(router)
        dp.include_router(quiz_router)
        logger.info('included routers')
        await set_commands(bot)

        # удаляет все обновления, которые произошли после последнего завершения работы бота
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    except Exception as e:
        logger.critical(f"Бот не может быть запущен: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())