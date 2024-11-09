from functions import insert_data_from_json
from config_data.config import DATABASE_URL, engine, async_session


# Вызов функции импорта из файла в базу данных
async def start_import():
    async with async_session() as session:
        await insert_data_from_json(session, 'vocabulary.json')

# Run the import
import asyncio
asyncio.run(start_import())