from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession
from config_data.config import logger

from database.functions import get_all_themes
from config_data.config import DATABASE_URL, engine, async_session

def main_kb():
    kb_list = [
        [KeyboardButton(text="📚 Фраза дня")],
        [KeyboardButton(text="📖 Изучаем слова"), KeyboardButton(text="📝 Тренируем слова")],

    ]
    keyboard = ReplyKeyboardMarkup(
        keyboard=kb_list,
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder="Воспользуйтесь меню:"
    )
    return keyboard
# KeyboardButton(text="👤 О чём это всё")

async def theme_keyboard(session: async_session):  # Add the session argument
    """Builds a keyboard from the list of themes obtained in the get_all_themes function."""
    builder = ReplyKeyboardBuilder()
    async with async_session() as session:
        try:
            theme_list = await get_all_themes(session)
            for item in theme_list:
                builder.button(text=item.name)
        except Exception as e:
            logger.exception(f"Error getting themes: {e}")
            builder.button(text="Не удалось загрузить темы")

        builder.button(text='Назад')
        builder.adjust(2, 4, 2, 2, 4)
        return builder.as_markup(resize_keyboard=True)

# def create_spec_kb():
#     kb_list = [
#         [KeyboardButton(text="Отправить гео", request_location=True)],
#         [KeyboardButton(text="Поделиться номером", request_contact=True)],
#         [KeyboardButton(text="Отправить викторину/опрос", request_poll=KeyboardButtonPollType())]
#     ]
#     keyboard = ReplyKeyboardMarkup(keyboard=kb_list,
#                                    resize_keyboard=True,
#                                    one_time_keyboard=True,
#                                    input_field_placeholder="Воспользуйтесь специальной клавиатурой:")
#     return keyboard
