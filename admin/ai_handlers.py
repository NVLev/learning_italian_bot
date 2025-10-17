from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from services.openai_service import get_openai_service, is_openai_available
from database.db_helper import db_helper
from sqlalchemy import select
from model.model import Vocabulary
from reply_keyboard.rep_kb import ai_explain_kb, ai_example_kb

router = Router()

class AIStates(StatesGroup):
    waiting_for_word_explain = State()
    waiting_for_word_example = State()

@router.message(Command("explain"))
async def cmd_explain(message: Message, state: FSMContext):
    """
    Команда для объяснения слова с помощью AI.

    Использование: /explain <слово>
    Пример: /explain ciao
    """
    # Проверяем доступность OpenAI
    if not await is_openai_available():
        await message.answer(
            "❌ Функция объяснения слов временно недоступна. "
            "Попробуйте позже или используйте обычный словарь."
        )
        return

    # Получаем слово из аргументов команды
    args = message.text.split()
    if len(args) < 2:
        await message.answer("📝 Использование: /explain <слово>\nНапример: /explain ciao")
        return

    word = args[1].lower()


        # Показываем индикатор набора текста
    await message.bot.send_chat_action(message.chat.id, "typing")

    service = get_openai_service()
    explanation = await service.explain_word(
        italian_word=word,
        russian_translation=""  # AI сам определит перевод
    )

    if explanation:
        response = f"🤖 **Объяснение слова '{word}'**\n\n{explanation}"
        await message.answer(response, parse_mode="Markdown")
    else:
        await message.answer("❌ Не удалось получить объяснение. Попробуйте позже.")


@router.message(Command("ai_status"))
async def cmd_ai_status(message: Message):
    """
    Проверка статуса OpenAI сервиса.

    Показывает текущее состояние подключения к AI-сервису.
    """
    service = get_openai_service()
    status = "✅ Доступен" if service.enabled else "❌ Недоступен"

    response = (
        f"🤖 **Статус AI-сервиса**\n"
        f"• Сервис: {status}\n"
        f"• Ключ API: {'✅ Установлен' if service.api_key else '❌ Отсутствует'}"
    )

    if service.enabled:
        is_working = await service.check_api_key()
        response += f"\n• Подключение: {'✅ Работает' if is_working else '❌ Ошибка'}"

    await message.answer(response)


@router.message(Command("example"))
async def cmd_example(message: Message):
    """
    Генерация примера предложения с словом.

    Использование: /example <слово>
    Пример: /example amore
    """
    # Проверяем доступность OpenAI
    if not await is_openai_available():
        await message.answer(
            "❌ Функция генерации примеров временно недоступна."
        )
        return

    # Получаем слово из аргументов команды
    args = message.text.split()
    if len(args) < 2:
        await message.answer("📝 Использование: /example <слово>\nНапример: /example amore")
        return

    word = args[1].lower()


        # Показываем индикатор набора текста
    await message.bot.send_chat_action(message.chat.id, "typing")

    service = get_openai_service()
    example = await service.generate_example_sentence(word)

    if example:
        response = f"📝 **Пример со словом '{word}'**\n\n{example}"
        await message.answer(response, parse_mode="Markdown")
    else:
        await message.answer("❌ Не удалось сгенерировать пример. Попробуйте позже.")


@router.message(F.text == "🤖 Объяснить слово")
async def ai_explain_button(message: Message, state: FSMContext):
    """
    Обработчик кнопки 'Объяснить слово'.
    """
    if not await is_openai_available():
        await message.answer(
            "❌ Функция объяснения слов временно недоступна. "
            "Попробуйте позже или используйте обычный словарь.",
            reply_markup=main_kb()
        )
        return

    await message.answer(
        "📝 Введите слово для объяснения или выберите из примеров:",
        reply_markup=ai_explain_kb()
    )
    await state.set_state(AIStates.waiting_for_word_explain)


@router.message(F.text == "🔍 Статус AI")
async def ai_status_button(message: Message):
    """
    Обработчик кнопки 'Статус AI'.
    """
    service = get_openai_service()
    status = "✅ Доступен" if service.enabled else "❌ Недоступен"

    response = (
        f"🤖 **Статус AI-сервиса**\n"
        f"• Сервис: {status}\n"
        f"• Ключ API: {'✅ Установлен' if service.api_key else '❌ Отсутствует'}"
    )

    if service.enabled:
        is_working = await service.check_api_key()
        response += f"\n• Подключение: {'✅ Работает' if is_working else '❌ Ошибка'}"

    await message.answer(response)

@router.message(F.text == "📝 Пример со словом")
async def ai_example_button(message: Message, state: FSMContext):
    """
    ИСПРАВЛЕНО: Обработчик кнопки 'Пример с словом'.
    """
    if not await is_openai_available():
        await message.answer(
            "❌ Функция генерации примеров временно недоступна.",
            reply_markup=main_kb()
        )
        return

    await message.answer(
        "📝 Введите итальянское слово для генерации примера или выберите из списка:",
        reply_markup=ai_example_kb()
    )
    await state.set_state(AIStates.waiting_for_word_example)

@router.message(AIStates.waiting_for_word_explain)
async def process_word_explain(message: Message, state: FSMContext):
    """
    Обработчик ввода слова для объяснения.
    """
    if message.text == "Назад":
        await message.answer("Главное меню:", reply_markup=main_kb())
        await state.clear()
        return

    # Извлекаем слово из текста
    word = message.text.replace("Объяснить: ", "").strip().lower()


    await message.bot.send_chat_action(message.chat.id, "typing")

    service = get_openai_service()
    explanation = await service.explain_word(
        italian_word=word,
        russian_translation=""  # AI сам определит
    )

    if explanation:
        response = f"🤖 **Объяснение слова '{word}'**\n\n{explanation}"
        await message.answer(response, reply_markup=main_kb(), parse_mode="Markdown")
    else:
        await message.answer(
            "❌ Не удалось получить объяснение. Попробуйте позже.",
            reply_markup=main_kb()
        )

    await state.clear()


@router.message(AIStates.waiting_for_word_example)
async def process_word_example(message: Message, state: FSMContext):
    """
    Обработчик ввода слова для генерации примера.
    """
    if message.text == "Назад":
        await message.answer("Главное меню:", reply_markup=main_kb())
        await state.clear()
        return

    # Извлекаем слово из текста (убираем "Пример: " если есть)
    word = message.text.replace("Пример: ", "").strip().lower()

    await message.bot.send_chat_action(message.chat.id, "typing")

    service = get_openai_service()
    example = await service.generate_example_sentence(word)

    if example:
        response = f"📝 **Пример со словом '{word}'**\n\n{example}"
        await message.answer(response, reply_markup=main_kb(), parse_mode="Markdown")
    else:
        await message.answer(
            "❌ Не удалось сгенерировать пример. Попробуйте позже.",
            reply_markup=main_kb()
        )

    await state.clear()

# ДОБАВИТЬ импорт главной клавиатуры в конец файла
from reply_keyboard.rep_kb import main_kb

