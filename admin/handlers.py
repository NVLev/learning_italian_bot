from aiogram import types, F, Router
from aiogram.types import Message
from aiogram.filters import Command

# создаём роутер для дальнешей привязки к нему обработчиков
router = Router()


# Декоратор @router.message означает, что функция является обработчиком входящих сообщений
@router.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Benvenuto! Я помогу тебе изучать итальянский.")


@router.message()
async def message_handler(msg: Message):
    await msg.answer(f"Твой ID: {msg.from_user.id}")
