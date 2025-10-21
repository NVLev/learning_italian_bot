"""
Middleware для автоматической регистрации/обновления пользователей.
"""
from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, User as TelegramUser, Message, CallbackQuery, TelegramObject
from services.user_service import UserService
from config_data.config import logger



class UserMiddleware(BaseMiddleware):
    """
    Middleware для автоматической регистрации пользователей в БД.
    Запускается при каждом обращении к боту.
    """

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Any:
        """
        Перехватывает все события и регистрирует пользователя.
        """
        # Получаем Telegram user из события
        telegram_user = None

        if hasattr(event, 'from_user') and event.from_user:
            telegram_user = event.from_user
        else:
            # Пробуем альтернативный способ через data
            telegram_user = data.get("event_from_user")

        if telegram_user and not telegram_user.is_bot:
            session = data.get("session")

            if session:
                try:
                    # Автоматически создаём/обновляем пользователя
                    db_user = await UserService.get_or_create_user(
                        session=session,
                        telegram_id=telegram_user.id,
                        username=telegram_user.username,
                        first_name=telegram_user.first_name,
                        last_name=telegram_user.last_name
                    )

                    # Добавляем user в data для использования в handlers
                    data["db_user"] = db_user

                except Exception as e:
                    logger.error(f"Error in UserMiddleware: {e}")

        # Продолжаем обработку события
        return await handler(event, data)