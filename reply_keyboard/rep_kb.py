from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession
from config_data.config import logger
from database.functions import get_all_themes

def main_kb():
    kb_list = [
        [KeyboardButton(text="📚 Фраза дня")],
        [KeyboardButton(text="📖 Изучаем слова"), KeyboardButton(text="📝 Тренируем слова")],
        [KeyboardButton(text="🤖 Объяснить слово"), KeyboardButton(text="📝 Пример со словом")],
        [KeyboardButton(text="🔍 Статус AI")]

    ]
    keyboard = ReplyKeyboardMarkup(
        keyboard=kb_list,
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder="Воспользуйтесь меню:"
    )
    return keyboard
# KeyboardButton(text="👤 О чём это всё")

async def theme_keyboard(session: AsyncSession)-> ReplyKeyboardMarkup:
    """Создает клавиатуру с темами из БД."""
    builder = ReplyKeyboardBuilder()

    try:
        themes = await get_all_themes(session)
        for theme in themes:
            builder.add(KeyboardButton(text=theme.name))

    except Exception as e:
        logger.error(f"Ошибка получения тем: {str(e)}")
        builder.add(KeyboardButton(text="⚠️ Ошибка загрузки"))

    builder.button(text='Назад')
    builder.adjust(2, 4, 2, 2, 4)
    return builder.as_markup(resize_keyboard=True,
                             input_field_placeholder="Выберите тему:")


def ai_explain_kb():
    """
    Клавиатура для функции объяснения слов.

    Returns:
        ReplyKeyboardMarkup: Клавиатура с примерами слов для объяснения
    """
    kb_list = [
        [KeyboardButton(text="Объяснить: ciao"), KeyboardButton(text="Объяснить: amore")],
        [KeyboardButton(text="Объяснить: grazie"), KeyboardButton(text="Объяснить: per favore")],
        [KeyboardButton(text="Назад")]
    ]
    keyboard = ReplyKeyboardMarkup(
        keyboard=kb_list,
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder="Выберите слово или введите своё:"
    )
    return keyboard


def ai_example_kb():
    """
    Клавиатура для функции генерации примеров.

    Returns:
        ReplyKeyboardMarkup: Клавиатура с примерами слов
    """
    kb_list = [
        [KeyboardButton(text="Пример: casa"), KeyboardButton(text="Пример: tempo")],
        [KeyboardButton(text="Пример: lavoro"), KeyboardButton(text="Пример: bello")],
        [KeyboardButton(text="Назад")]
    ]
    keyboard = ReplyKeyboardMarkup(
        keyboard=kb_list,
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder="Выберите слово или введите своё:"
    )
    return keyboard
