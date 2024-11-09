import random

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from inline_keyboard.inline_kb_w_call_back import theme_keyboard
from reply_keyboard.rep_kb import main_kb
from aiogram.filters import Command
from config_data.config import logger, async_session
from database.functions import get_all_themes, get_words_by_theme_id, get_all_idioms
from aiogram.fsm.context import FSMContext
from utils.states import Quiz
from functions_for_handler.admin_functions import format_word_list


router = Router()



# async def process_theme_selection(callback_query: CallbackQuery, filter:ThemeFilter):
#     theme_name = filter.theme_name
#     async with async_session() as session:
#         try:
#             words = await get_words_by_theme(session=async_session, theme_name=theme_name)
#             # Обрабатываем список слов
#             await callback_query.message.answer("\n".join([f"{word.italian_word} - {word.rus_word}" for word in words]))
#         except Exception as e:
#             await callback_query.message.answer(f"An error occurred: {e}")


# Фильтр для обработки нажатия на определенную тему, если выбрано - "Изучаем слова"
# (т.е. состояние - no_quiz)- выводится список слов по теме
@router.callback_query(F.data.in_({str(i) for i in range(1, 19)}), Quiz.no_quiz)
async def demonstrating_word_by_theme(callback: CallbackQuery, state: FSMContext):
    logger.info('started with word list')
    await state.clear()
    async with async_session() as session:
        try:
            # logger.info(callback.data)
            words = await get_words_by_theme_id(int(callback.data))
            # logger.info(words)
            await callback.message.answer(
                "\n".join([f"• {word.italian_word}    ➔    {word.rus_word}" for word in words]))
            # await callback.message.answer(
                # "\n".join([f"📝 {word.italian_word.ljust(30)} │ {word.rus_word}" for word in words]))
            # await callback.message.answer(format_word_list(words))
            # await callback.message.answer("\n".join([f"{word.italian_word} - {word.rus_word}" for word in words]))


        except Exception as e:
            logger.error(f"Ошибка в demonstrating_word_by_theme: {e}")
            await callback.message.answer("Ошибка")

        finally:
            await session.close()

@router.message(F.text.startswith("📚 Фраза дня"))
async def cmd_idiom(message: Message, state: FSMContext):
    await state.set_state(Quiz.idiom)
    logger.info('idioms_started')
    async with async_session() as session:
        try:
            idioms = await get_all_idioms(session)
            current_idiom = random.choice(idioms)
            await message.answer(f'{current_idiom.italian_idiom} - {current_idiom.rus_idiom}')
        except Exception as e:
            logger.error(f"Error in cmd_idiom: {e}")
            await message.answer("Произошла ошибка, сегодня фразы нет")
        finally:
            await session.close()

@router.message(F.text.startswith("📖 Изучаем слова"))
@router.message(Command('learn'))
async def cmd_learn(message: Message, state: FSMContext):
    await state.set_state(Quiz.no_quiz)
    logger.info('state - no_quiz is set')
    async with async_session() as session:
        try:
            themes = await get_all_themes(session)
            keyboard = await theme_keyboard(themes)
            await message.answer('Выберите тему',
                               reply_markup=keyboard)
        except Exception as e:
            logger.error(f"Ошибка в cmd_learn: {e}")
            await message.answer("Ошибка.")
        finally:
            await session.close()

@router.message(F.text.startswith("📝 Тренируем слова"))
@router.message(Command('train'))
async def cmd_train(message: Message, state: FSMContext):
    await state.set_state(Quiz.quiz_start)
    logger.info('state - quiz_start is set')
    async with async_session() as session:
        try:
            themes = await get_all_themes(session)
            keyboard = await theme_keyboard(themes)  # Pass themes instead of session
            await message.answer('На какую тему будем тренироваться?  Выберите из тем ниже',
                               reply_markup=keyboard)
        except Exception as e:
            logger.error(f"Ошибка в cmd_train: {e}")
            await message.answer("Ошибка.")
        finally:
            await session.close()
            current_state = await state.get_state()
            logger.info(current_state)


@router.callback_query(F.data == 'back')
async def handle_back_button(callback_query: CallbackQuery):
    await callback_query.answer('Вы вернулись в главное меню',
                                reply_markup=main_kb())


@router.message()
async def echo_message(msg: Message):
    logger.info('echo started')
    await msg.answer(f'{msg.text} - такой команды нет, выберите команду в меню')
