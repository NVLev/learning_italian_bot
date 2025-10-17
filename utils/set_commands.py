from aiogram import types, Bot
from aiogram.types import BotCommand

async def set_commands(bot: Bot):
    commands = [
        BotCommand(command='start', description='🚀 Запуск бота'),
        BotCommand(command='help', description='💡 Обзор команд'),
        BotCommand(command='learn', description='📖 Изучаем слова'),
        BotCommand(command='train', description='📝 Тренируем слова'),
        BotCommand(command="explain", description="🤖 Объяснить слово (AI)"),
        BotCommand(command="example", description="📝 Пример со словом (AI)"),
        BotCommand(command="ai_status", description="🔍 Статус AI"),
    ]
    await bot.set_my_commands(commands)


