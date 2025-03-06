import os
from database.functions import insert_data_from_json, insert_idioms_from_json
from database.db_helper import db_helper
from config_data.config import logger

# Вызов функции импорта из файла в базу данных
async def start_import():
    async with db_helper.get_session() as session:
        try:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Путь к корню проекта
            vocab_path = os.path.join(base_dir, "database", "vocabulary.json")
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Путь к корню проекта
            idiom_path = os.path.join(base_dir, "database", "italian_idioms.json")

            await insert_data_from_json(session, vocab_path)


            # Импорт идиом
            await insert_idioms_from_json(session, idiom_path)

            logger.info("Данные успешно импортированы")
        except Exception as e:
            logger.error(f"Ошибка импорта: {str(e)}")
            raise

if __name__ == "__main__":
    import asyncio
    asyncio.run(start_import())
# from functions import insert_data_from_json
# from config_data.config import DATABASE_URL, engine, async_session
#
#
# # Вызов функции импорта из файла в базу данных
# async def start_import():
#     async with async_session() as session:
#         await insert_data_from_json(session, 'vocabulary.json')
#
#
# import asyncio
# asyncio.run(start_import())