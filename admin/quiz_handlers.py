import random
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone

from config_data.config import logger
from database.functions import get_words_by_theme_id
from inline_keyboard.inline_kb_w_call_back import (
    create_quiz_keyboard,
    create_next_question_keyboard,
    generate_quiz_options
)
from utils.states import Quiz
from services.user_service import UserService
from model.model import User, Vocabulary



quiz_router = Router()



@quiz_router.callback_query(F.data.in_({str(i) for i in range(1, 19)}), Quiz.quiz_start)
async def quiz_word_by_theme(
        callback: CallbackQuery,
        state: FSMContext,
        session: AsyncSession,
        db_user: User | None = None
):
    """
    Квиз - выбор слова и генерация вопроса
    """
    logger.info('quiz filter worked')
    current_state = await state.get_state()
    logger.info(f'Current state: {current_state}')
    if db_user is None:
        # Если middleware не передал пользователя — создаем / достаем его вручную
        logger.warning("db_user not found in data, fetching from DB via UserService.get_or_create_user()")
        user = await UserService.get_or_create_user(
            session=session,
            telegram_id=callback.from_user.id,
            username=callback.from_user.username,
            first_name=callback.from_user.first_name
        )
    else:
        user = db_user

    try:
        theme_id = int(callback.data)
        logger.info(f"Starting quiz for theme_id={theme_id}")

        words = await get_words_by_theme_id(session, theme_id)
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

        # Инициализируем данные сессии при первом вопросе
        user_data = await state.get_data()
        if not user_data.get('session_started'):
            await state.update_data(
                session_started=True,
                session_start_time=datetime.now(timezone.utc),
                correct_count=0,
                wrong_count=0,
                theme_id=theme_id
            )

        # Сохраняем ID текущего слова для отслеживания прогресса
        await state.update_data(
            correct_answer=current_word.rus_word,
            italian_word=current_word.italian_word,
            current_word_id=current_word.id  # ← ВАЖНО! Сохраняем ID
        )

        # Отправляем вопрос
        await callback.message.answer(
            f"Выберите правильный перевод слова:\n\n<b>{current_word.italian_word}</b>",
            reply_markup=keyboard,
            parse_mode="HTML"
        )
        await callback.answer()

    except Exception as e:
        logger.error(f"Error in quiz_word_by_theme: {e}", exc_info=True)
        await callback.message.answer("Произошла ошибка при создании вопроса")


@quiz_router.callback_query(F.data.startswith("answer_"))
async def check_answer(
        callback: CallbackQuery,
        state: FSMContext,
        session: AsyncSession,
        db_user: User | None = None
):
    """
    Обработчик проверки ответа:
    - Анализирует выбор пользователя
    - Сохраняет прогресс по слову
    - Обновляет статистику сессии
    - Предлагает продолжить
    """
    if db_user is None:
        user = await UserService.get_or_create_user(
            session=session,
            telegram_id=callback.from_user.id,
            username=callback.from_user.username,
            first_name=callback.from_user.first_name
        )
    else:
        user = db_user
    try:
        # Парсим callback data
        data = callback.data.split("_")
        is_correct_int = int(data[1])
        theme_id = data[2]

        # Преобразуем в bool
        is_correct = is_correct_int == 1

        # Получаем данные из состояния
        user_data = await state.get_data()
        correct_answer = user_data.get("correct_answer", "неизвестно")
        italian_word = user_data.get("italian_word", "")
        current_word_id = user_data.get('current_word_id')

        # Обновляем счетчики сессии
        correct_count = user_data.get('correct_count', 0)
        wrong_count = user_data.get('wrong_count', 0)

        if is_correct:
            correct_count += 1
            response = "✅ <b>Правильно!</b> Молодец!"
        else:
            wrong_count += 1
            response = (
                f"❌ <b>Неправильно!</b>\n\n"
                f"<i>{italian_word}</i> = <b>{correct_answer}</b>"
            )

        # Сохраняем обновленные счетчики
        await state.update_data(
            correct_count=correct_count,
            wrong_count=wrong_count
        )

        # Сохраняем прогресс по слову (если есть word_id)
        if current_word_id:
            try:
                await UserService.update_word_progress(
                    session=session,
                    user_id=db_user.id,
                    word_id=current_word_id,
                    is_correct=is_correct
                )
                logger.info(
                    f"Progress saved: user={db_user.id}, word={current_word_id}, "
                    f"correct={is_correct}"
                )
            except Exception as e:
                logger.error(f"Error saving word progress: {e}")
        else:
            logger.warning("current_word_id not found in state")

        # Показываем статистику сессии
        total = correct_count + wrong_count
        accuracy = (correct_count / total * 100) if total > 0 else 0

        response += (
            f"\n\n📊 <b>Статистика сессии:</b>\n"
            f"✅ Правильно: {correct_count}\n"
            f"❌ Ошибок: {wrong_count}\n"
            f"🎯 Точность: {accuracy:.0f}%"
        )

        await callback.message.answer(response, parse_mode="HTML")

        # Предлагаем продолжить
        await callback.message.answer(
            "Хотите попробовать еще раз?",
            reply_markup=create_next_question_keyboard(theme_id)
        )

        await callback.answer()

    except Exception as e:
        logger.error(f"Error in check_answer: {e}", exc_info=True)
        await callback.message.answer("Произошла ошибка при обработке ответа")


@quiz_router.callback_query(F.data == "back", Quiz.quiz_start)
async def end_quiz_session(
        callback: CallbackQuery,
        state: FSMContext,
        db_user: User,
        session: AsyncSession
):
    """
    ДОБАВЛЕНО: Завершение квиза и сохранение сессии
    """
    try:
        user_data = await state.get_data()

        # Проверяем что сессия была начата
        if not user_data.get('session_started'):
            await callback.message.answer("Квиз не был начат")
            await state.clear()
            return

        correct_count = user_data.get('correct_count', 0)
        wrong_count = user_data.get('wrong_count', 0)
        theme_id = user_data.get('theme_id')
        session_start_time = user_data.get('session_start_time')

        # Рассчитываем длительность
        duration_seconds = None
        if session_start_time:
            duration = datetime.now(timezone.utc) - session_start_time
            duration_seconds = int(duration.total_seconds())

        # Сохраняем тренировочную сессию
        if correct_count > 0 or wrong_count > 0:
            await UserService.save_training_session(
                session=session,
                user_id=db_user.id,
                session_type='quiz',
                theme_id=theme_id,
                correct_answers=correct_count,
                wrong_answers=wrong_count,
                duration_seconds=duration_seconds
            )

            # Показываем итоги
            total = correct_count + wrong_count
            accuracy = (correct_count / total * 100) if total > 0 else 0

            response = (
                f"🎉 <b>Квиз завершен!</b>\n\n"
                f"📊 <b>Твои результаты:</b>\n"
                f"✅ Правильно: {correct_count}\n"
                f"❌ Ошибок: {wrong_count}\n"
                f"🎯 Точность: {accuracy:.0f}%\n"
                f"⏱ Время: {duration_seconds // 60} мин {duration_seconds % 60} сек\n\n"
                f"⭐ Получено опыта: {correct_count * 10 + wrong_count * 2} XP"
            )

            await callback.message.answer(response, parse_mode="HTML")
            logger.info(f"Quiz session saved for user {db_user.id}")

        await state.clear()
        await callback.answer("Квиз завершен")

    except Exception as e:
        logger.error(f"Error in end_quiz_session: {e}", exc_info=True)
        await callback.message.answer("Ошибка при сохранении результатов")
        await state.clear()