import random

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession
from config_data.config import logger
from database.functions import get_words_by_theme_id
from inline_keyboard.inline_kb_w_call_back import (
    create_quiz_keyboard,
    create_next_question_keyboard,
    generate_quiz_options
)
from utils.states import Quiz

quiz_router = Router()


# Фильтр для обработки нажатия на определенную тему, если выбрано - "Тренируем слова"
# (т.е. состояние - quiz_start)- выводится итальянское слово
@quiz_router.callback_query(F.data.in_({str(i) for i in range(1, 19)}), Quiz.quiz_start)
async def quiz_word_by_theme(
    callback: CallbackQuery,
    state: FSMContext,
    session: AsyncSession  # Инжектируем сессию
):
    """
    Квиз
    - берём список слов по тебе из БД (та же функция, что и в "Изучаем слова)
    - рандомно выбираем из него одну пару ит-рус
    - передаём в клавиатуру правильный ответ + 3 рандомных
    - записываем в состояние правильный ответ
    - выводим клавиатуру
    """
    logger.info('filter worked')
    current_state = await state.get_state()
    logger.info(f'{current_state}')
    try:
        logger.info(callback.data)
        words = await get_words_by_theme_id(session, int(callback.data))
        if not words:
            await callback.message.answer("В этой теме пока нет слов для тренировки 😔")
            return
        # Формируем вопрос
        current_word = random.choice(words)

        possible_answers = generate_quiz_options(words, current_word)
        keyboard = create_quiz_keyboard(
            possible_answers=possible_answers,
            correct_answer=current_word.rus_word,
            theme_id=callback.data,

        )
        # Сохраняем данные в состоянии
        await state.update_data(correct_answer=current_word.rus_word,
                                theme_id=callback.data,
                                italian_word=current_word.italian_word )
        # Отправляем вопрос
        await callback.message.answer(
            f"Выберите правильный перевод слова:\n\n{current_word.italian_word}",
            reply_markup=keyboard
        )

    except Exception as e:
        logger.error(f"Error in quiz_word_by_theme: {e}")
        await callback.message.answer("Произошла ошибка при создании вопроса")



@quiz_router.callback_query(F.data.startswith("answer_"))
async def check_answer(
    callback: CallbackQuery,
    state: FSMContext,
    session: AsyncSession  # Добавляем сессию для будущего использования
):
    """
        Обработчик проверки ответа:
        - Анализирует выбор пользователя
        - Показывает правильный ответ
        - Предлагает продолжить
        """
    try:
        data = callback.data.split("_")
        is_correct = int(data[1])
        theme_id = data[2]
        # Получаем данные из состояния
        user_data = await state.get_data()
        correct_answer = user_data.get("correct_answer", "неизвестно")

        if is_correct:
            await callback.message.answer("Правильно! Молодец!")
        else:
            await callback.message.answer(f"Неправильно! Правильный ответ: {correct_answer}")

        await callback.message.answer("Хотите попробовать еще раз?",
                                      reply_markup=create_next_question_keyboard(theme_id))
    except Exception as e:
        logger.error(f"Error in check_answer: {e}")
        await callback.message.answer("Произошла ошибка при обработке ответа")

    # await state.clear()
