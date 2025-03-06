from aiogram import BaseMiddleware
from typing import Callable, Awaitable, Any
from aiogram.types import Message
from database.db_helper import db_helper

class DatabaseMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: dict[str, Any]
    ) -> Any:
        async with db_helper.get_session() as session:  # Теперь работает корректно
            data["session"] = session
            return await handler(event, data)