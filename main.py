import asyncio
from loader import bot, dp
from admin.handlers import router
import logging


async def main():
    # подключает к диспетчеру все обработчики, которые используют router
    dp.include_router(router)
    # удаляет все обновления, которые произошли после последнего завершения работы бота
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())