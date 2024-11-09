from aiogram import types, Bot
from aiogram.types import BotCommand

async def set_commands(bot: Bot):
    commands = [
        BotCommand(command='start', description='🚀 Запуск бота'),
        BotCommand(command='help', description='\U0001F4A1 Обзор команд'),
        BotCommand(command='learn', description='📖 Изучаем слова'),
        BotCommand(command='train', description='📝 Тренируем слова'),
    ]
    await bot.set_my_commands(commands)


