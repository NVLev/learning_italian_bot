import random
from typing import List

from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


async def theme_keyboard(themes) -> InlineKeyboardMarkup:
    """
    Строит клавиатуру на основе списка тем
    """
    builder = InlineKeyboardBuilder()

    if not themes:
        builder.add(InlineKeyboardButton(
            text="Темы отсутствуют",
            callback_data="no_themes"
        ))
    else:
        for theme in themes:
            callback_data = str(theme.id)
            builder.add(InlineKeyboardButton(
                text=theme.name,
                callback_data=callback_data
            ))
            # logger.info(callback_data)

    builder.add(InlineKeyboardButton(
        text='Назад',
        callback_data="back"
    ))
    builder.adjust(2, 4, 2, 2, 4)
    return builder.as_markup(resize_keyboard=True)


def create_quiz_keyboard(possible_answers: list, correct_answer: str, theme_id: str) -> InlineKeyboardMarkup:
    """
    Создает клавиатуру с 4 возможными ответами
    """
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=answer,
                              callback_data=f"answer_{1 if answer == correct_answer else 0}_{theme_id}")]
        for answer in possible_answers
    ])


def create_next_question_keyboard(theme_id: str) -> InlineKeyboardMarkup:
    """
    Создает клавиатуру с кнопкой "Следующий вопрос"
    """
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="Следующий вопрос", callback_data=theme_id)
    ]])


def generate_quiz_options(words: list, current_word) -> list:
    """
    Генерирует список  из 4 слов в квизе (1 правильный + 3 случайных)
    """
    possible_answers = [current_word.rus_word]

    other_words = [word for word in words if word.rus_word != current_word.rus_word]
    if len(other_words) >= 3:
        random_words = random.sample(other_words, 3)
        possible_answers.extend([word.rus_word for word in random_words])
    else:
        while len(possible_answers) < 4:
            possible_answers.append(random.choice(other_words).rus_word)

    random.shuffle(possible_answers)
    return possible_answers

    # return builder.as_markup(resize_keyboard=True)