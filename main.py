import asyncio

from aiogram.filters import Command
import logging
from admin.handlers import router
from loader import bot, dp
from admin.ai_handlers import router as ai_router
from admin.start_handlers import start_router
from admin.quiz_handlers import quiz_router
from db_config.db_config import settings
from config_data.config import logger
from utils.set_commands import set_commands
from middleware.middleware import DatabaseMiddleware
from model.model import Base
from database.db_main import start_import



async def main():
    try:
        logger.info("Checking database and importing data if needed...")
        await start_import()

        dp.update.middleware(DatabaseMiddleware())
        logger.info('middleware registered')
        dp.include_router(start_router)
        dp.include_router(router)
        dp.include_router(quiz_router)
        dp.include_router(ai_router)
        logger.info('routers included')
        await set_commands(bot)

        # удаляет все обновления, которые произошли после последнего завершения работы бота
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    except Exception as e:
        logger.critical(f"Бот не может быть запущен: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())