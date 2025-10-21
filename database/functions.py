import json
from typing import Any

from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError, IntegrityError, NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession


from config_data.config import logger
from model.model import Theme, Vocabulary, Idiom
from schemas.schemas import ThemeRead, VocabularyRead, IdiomRead


async def get_words_by_theme_id(
    session: AsyncSession,  # Принимаем сессию извне
    theme_id: int
) -> list[Vocabulary] | list[Any]:
    """
    Функция получает список слов в зависимости от темы
    """
    try:
        stmt = select(Vocabulary).where(Vocabulary.theme_id == theme_id)
        result = await session.execute(stmt)
        words = list(result.scalars().all())

        logger.info(f"Found {len(words)} words for theme_id {theme_id}")
        return words

    except NoResultFound:
        logger.warning(f"No words found for theme: {theme_id}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error in get_words_by_theme_id: {e}")
        return []
    # try:
    #     stmt = select(Vocabulary).join(Theme).filter(Theme.id == theme_id)
    #     result = await session.execute(stmt)
    #     words = result.scalars().all()
    #
    #     words_reads = []
    #     for word in words:
    #         try:
    #             words_read = VocabularyRead(italian_word=word.italian_word, rus_word=word.rus_word)
    #             logger.info(f"Reading word: {words_read}")
    #             words_reads.append(words_read)
    #         except ValidationError as e:
    #             logger.error(f"Pydantic validation error for word: {word}, Error: {e}")
    #
    #     return words_reads
    except NoResultFound:
        logger.warning(f"No words found for theme: {theme_id}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error in get_words_by_theme_id: {e}")
        return []

async def get_words_by_theme_id_as_schemas(
    session: AsyncSession,
    theme_id: int
) -> list[VocabularyRead]:
    """
    Альтернативная функция: возвращает слова как схемы Pydantic
    """
    try:
        stmt = select(Vocabulary).where(Vocabulary.theme_id == theme_id)
        result = await session.execute(stmt)
        words = result.scalars().all()

        words_reads = []
        for word in words:
            try:
                # Используем model_validate с полными данными
                word_data = {
                    'id': word.id,
                    'italian_word': word.italian_word,
                    'rus_word': word.rus_word,
                    'theme_id': word.theme_id,
                    'difficulty': word.difficulty,
                    'usage_example': word.usage_example
                }
                words_read = VocabularyRead.model_validate(word_data)
                words_reads.append(words_read)
            except ValidationError as e:
                logger.error(f"Pydantic validation error for word: {word}, Error: {e}")

        return words_reads
    except Exception as e:
        logger.error(f"Unexpected error in get_words_by_theme_id_as_schemas: {e}")
        return []

async def get_all_themes(session: AsyncSession) -> list[ThemeRead] | list[Any]:
    """
    Функция получает список тем
    """
    try:
        stmt = select(Theme).order_by(Theme.id)
        result = await session.execute(stmt)
        themes = list(result.scalars().all())

        theme_reads = []
        for theme in themes:
            try:
                theme_read = ThemeRead.model_validate({
                    'id': theme.id,
                    'name': theme.name
                })
                # logger.info(f'Reading theme is {theme.name}')
                theme_reads.append(theme_read)

            except ValidationError as e:
                logger.error(f"Pydantic validation error for theme {theme.name}: {e}")
                continue
        return theme_reads

    except SQLAlchemyError as e:
        logger.exception(f"Database error in get_all_themes: {e}")
        return []
    except Exception as e:
        logger.exception(f"An unexpected error occurred in get_all_themes: {e}")
        return []

async def get_all_idioms(session: AsyncSession) -> list[IdiomRead] | list[Any]:
    """
    Функция получает идиомы
    """
    try:
        stmt = select(Idiom)
        result = await session.execute(stmt)
        idioms = list(result.scalars().all())

        idiom_reads = []
        for idiom in idioms:
            try:
                idiom_read = IdiomRead.model_validate({
                    'italian_idiom': idiom.italian_idiom,
                    'rus_idiom': idiom.rus_idiom
                })
                logger.info(f'Reading idiom is {idiom.rus_idiom}, {idiom.italian_idiom}')
                idiom_reads.append(idiom_read)
            except ValidationError as e:
                logger.error(f"Pydantic error for idiom ID {idiom.id}: {e}")
                continue
        # logger.info(idiom_reads)
        return idiom_reads

    except SQLAlchemyError as e:
        logger.exception(f"Database error in get_all_themes: {e}")
        return []
    except Exception as e:
        logger.exception(f"An unexpected error occurred in get_all_themes: {e}")
        return []

async def get_theme_name_by_id(session: AsyncSession, id: int):
    pass

async def insert_data_from_json(session: AsyncSession, json_file_path: str):
    """
    Вставляет данные из подготовленного JSON файла в базу данных
    """
    try:

        with open(json_file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        for theme_name, words in data.items():

            theme = Theme(name=theme_name)
            session.add(theme)
            try:
                await session.flush()  # Flush to get theme.id
            except IntegrityError:

                await session.rollback()
                stmt = select(Theme).where(Theme.name == theme_name)
                result = await session.execute(stmt)
                logger.info(f"Processing theme: {theme_name}")
                theme = result.scalar_one()


            for word in words:
                vocabulary = Vocabulary(
                    italian_word=word['italian'],
                    rus_word=word['russian'],
                    theme_id=theme.id
                )
                session.add(vocabulary)


        await session.commit()

        return {"message": "Data inserted successfully"}

    except Exception as e:
        await session.rollback()
        raise Exception(f"Error inserting data: {str(e)}")


# Helper function to check if theme exists
async def get_theme_by_name(session: AsyncSession, theme_name: str) -> Theme:
    """
    Get theme by name
    """
    stmt = select(Theme).where(Theme.name == theme_name)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def insert_idioms_from_json(session: AsyncSession, json_file_path: str):
    """
    Вставляет данные из подготовленного JSON файла в базу данных
    """
    try:

        with open(json_file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)


        if not isinstance(data, list):
            raise ValueError("JSON data must be a list of idiom pairs")


        for idiom_data in data:
            idiom_phrase = Idiom(
                italian_idiom=idiom_data['italian'],
                rus_idiom=idiom_data['russian']
            )
            session.add(idiom_phrase)

        await session.commit()
        return {"message": "Data inserted successfully"}

    except FileNotFoundError:
        await session.rollback()
        raise Exception(f"JSON file not found: {json_file_path}")
    except json.JSONDecodeError:
        await session.rollback()
        raise Exception("Invalid JSON format")
    except KeyError as e:
        await session.rollback()
        raise Exception(f"Missing required field: {str(e)}")
    except Exception as e:
        await session.rollback()
        raise Exception(f"Error inserting data: {str(e)}")


# async def main():
#     async with async_session() as session:
#         result = await insert_idioms_from_json(session, "italian_idioms.json")
#         print(result)
async def main(session: AsyncSession):
    result = await get_all_idioms(session)
    print(result)


# import asyncio
# asyncio.run(main())