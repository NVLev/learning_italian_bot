import random

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from inline_keyboard.inline_kb_w_call_back import theme_keyboard
from reply_keyboard.rep_kb import main_kb
from aiogram.filters import Command
from config_data.config import logger
from sqlalchemy.ext.asyncio import AsyncSession
from database.functions import get_all_themes, get_words_by_theme_id, get_all_idioms
from aiogram.fsm.context import FSMContext
from utils.states import Quiz
from functions_for_handler.admin_functions import format_word_list


router = Router()



# Фильтр для обработки нажатия на определенную тему, если выбрано - "Изучаем слова"
# (т.е. состояние - no_quiz)- выводится список слов по теме
@router.callback_query(F.data.in_({str(i) for i in range(1, 19)}), Quiz.no_quiz)
async def demonstrating_word_by_theme(
    callback: CallbackQuery,
    state: FSMContext,
    session: AsyncSession  # Добавляем инжекцию сессии
):
    logger.info('started with word list')
    await state.clear()
    try:
        words = await get_words_by_theme_id(session, int(callback.data))  # Передаем сессию

        # Преобразуем объекты VocabularyRead в строки
        formatted_words = [
            f"🇮🇹 {word.italian_word} ➔ 🇷🇺 {word.rus_word}"
            for word in words
        ]

        if not formatted_words:
            await callback.message.answer("В этой теме пока нет слов 😔")
            return

        await callback.message.answer("\n".join(formatted_words))

    except Exception as e:
        logger.error(f"Ошибка в demonstrating_word_by_theme: {e}")
        await callback.message.answer("Ошибка")
        # Убираем finally с session.close()



@router.message(F.text.startswith("📚 Фраза дня"))
async def cmd_idiom(
    message: Message,
    state: FSMContext,
    session: AsyncSession  # Инжектируем сессию
):
    await state.set_state(Quiz.idiom)
    logger.info('idioms_started')

    try:
        idioms = await get_all_idioms(session)
        current_idiom = random.choice(idioms)
        await message.answer(f'{current_idiom.italian_idiom} - {current_idiom.rus_idiom}')
    except Exception as e:
        logger.error(f"Error in cmd_idiom: {e}")
        await message.answer("Произошла ошибка, сегодня фразы нет")

@router.message(F.text.startswith("📖 Изучаем слова"))
@router.message(Command('learn'))
async def cmd_learn(
    message: Message,
    state: FSMContext,
    session: AsyncSession  # Добавляем сессию
):
    await state.set_state(Quiz.no_quiz)
    logger.info('state - no_quiz is set')

    try:
        themes = await get_all_themes(session)
        keyboard = await theme_keyboard(themes)
        await message.answer('Выберите тему',
                           reply_markup=keyboard)
    except Exception as e:
        logger.error(f"Ошибка в cmd_learn: {e}")
        await message.answer("Ошибка.")


@router.message(F.text.startswith("📝 Тренируем слова"))
@router.message(Command('train'))
async def cmd_train(
        message: Message,
        state: FSMContext,
        session: AsyncSession
):
    await state.set_state(Quiz.quiz_start)
    logger.info('state - quiz_start is set')

    try:
        themes = await get_all_themes(session)
        keyboard = await theme_keyboard(themes)
        await message.answer(
            'На какую тему будем тренироваться? Выберите из тем ниже',
            reply_markup=keyboard
        )
    except Exception as e:
        logger.error(f"Ошибка в cmd_train: {e}")
        await message.answer("Ошибка.")
    finally:
        current_state = await state.get_state()
        logger.info(f"Current state: {current_state}")  # Добавлен f-string


@router.callback_query(F.data == 'back')
async def handle_back_button(callback_query: CallbackQuery):
    await callback_query.answer('Вы вернулись в главное меню',
                                reply_markup=main_kb())


@router.message()
async def echo_message(msg: Message):
    logger.info('echo started')
    await msg.answer(f'{msg.text} - такой команды нет, выберите команду в меню')
