import os
from database.functions import insert_data_from_json, insert_idioms_from_json
from database.db_helper import db_helper
from sqlalchemy import select, func
from model.model import Vocabulary, Idiom
from config_data.config import logger  # Оставляем старый импорт логгера


async def check_if_data_exists() -> bool:
    """Проверить есть ли данные в БД"""
    async with db_helper.get_session() as session:
        try:
            # Проверяем есть ли хоть одно слово
            result = await session.execute(select(func.count()).select_from(Vocabulary))
            vocab_count = result.scalar()

            # Проверяем есть ли хоть одна идиома
            result = await session.execute(select(func.count()).select_from(Idiom))
            idiom_count = result.scalar()

            has_data = vocab_count > 0 and idiom_count > 0
            logger.info(f"Database check: {vocab_count} words, {idiom_count} idioms")

            return has_data
        except Exception as e:
            logger.warning(f"Error checking data existence: {e}")
            return False


async def start_import():
    """Вызов функции импорта из файла в базу данных"""

    # Проверяем, нужен ли импорт
    if await check_if_data_exists():
        logger.info("✓ Database already contains data, skipping import")
        return

    logger.info("Database is empty, starting import...")

    async with db_helper.get_session() as session:
        try:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            vocab_path = os.path.join(base_dir, "database", "vocabulary.json")
            idiom_path = os.path.join(base_dir, "database", "italian_idioms.json")

            # Проверяем что файлы существуют
            if not os.path.exists(vocab_path):
                logger.error(f"Vocabulary file not found: {vocab_path}")
                return

            if not os.path.exists(idiom_path):
                logger.error(f"Idioms file not found: {idiom_path}")
                return

            logger.info(f"Starting vocabulary import from {vocab_path}...")
            await insert_data_from_json(session, vocab_path)

            logger.info(f"Starting idioms import from {idiom_path}...")
            await insert_idioms_from_json(session, idiom_path)

            logger.info("✓ Data import completed successfully!")
        except Exception as e:
            logger.error(f"✗ Error during import: {str(e)}", exc_info=True)
            raise


if __name__ == "__main__":
    import asyncio

    asyncio.run(start_import())