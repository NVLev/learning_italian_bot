from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from config_data.config import logger
from loader import bot
from reply_keyboard.rep_kb import main_kb
from sqlalchemy.ext.asyncio import AsyncSession



# создаём роутер для дальнешей привязки к нему обработчиков
start_router = Router()


# Декоратор @router.message означает, что функция является обработчиком входящих сообщений
@start_router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer('Benvenuto! Я помогу тебе изучать итальянский',
                         reply_markup=main_kb())
    logger.info(f"User {message.from_user.id} started the bot")



@start_router.message(Command('help'))
async def cmd_help(message: Message):
    await message.answer('Этот бот поможет вам изучить лексику итальянского языка.'
            'Можете посмотреть слова по темам, нажав <b>📖 Изучаем слова.</b>'
            'Если хотите проверить знания, нажмите <b>📝 Тренируем слова.</b>'
            'А можно просто нажать <b>📚 Фраза дня</b>, и посмотреть, что за идиома вам выпадет сегодня',
                         reply_markup=main_kb())


