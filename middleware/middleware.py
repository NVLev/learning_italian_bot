from aiogram import BaseMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from config_data.config import DATABASE_URL, engine, async_session
from config_data.config import logger
#
# class DatabaseMiddleware(BaseMiddleware):
#     async def __call__(self, handler, event, data):
#         print(f"Data in middleware before handler call: {data}")
#         async with async_session() as session: #Use db_helper.session_getter
#             data["session"] = session
#             try:
#                 return await handler(event, data)
#             except Exception as e:
#                 # Handle exceptions appropriately (log, rollback, etc.)
#                 logger.exception(f"Error in handler: {e}")
#                 await session.rollback() #Roll back transaction in case of errors
