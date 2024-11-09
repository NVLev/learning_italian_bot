from aiogram.filters import BaseFilter
from aiogram import types
from aiogram.types import CallbackQuery


class ThemeFilter(BaseFilter):
    async def __call__(self, message: types.Message | CallbackQuery) -> bool:
        if isinstance(message, CallbackQuery):
            # достаем тему  (name) из callback data в меню
            theme_name = message.data.split(":")[1] if ":" in message.data else None
            if theme_name:
                # Передаем имя в функцию.  The function will need to be adapted to async context
                self.theme_name = theme_name
                return True
        return False