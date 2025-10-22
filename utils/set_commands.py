from aiogram import types, Bot
from aiogram.types import BotCommand

async def set_commands(bot: Bot):
    commands = [
        BotCommand(command='start', description='🚀 Запуск бота'),
        BotCommand(command='help', description='💡 Помощь и инструкции'),
        BotCommand(command="progress_help", description="О системе прогресса"),
        BotCommand(command='stats', description='📊 Моя статистика'),
        BotCommand(command='level', description='⭐ Мой уровень'),
        BotCommand(command='streak', description='🔥 Мой streak'),
        BotCommand(command='learn', description='📖 Изучаем слова'),
        BotCommand(command="explain", description="🤖 Объяснить слово (AI)"),
        BotCommand(command="example", description="📝 Пример со словом (AI)"),
        BotCommand(command="conversation", description="💬 Практика диалога (AI)"),
        BotCommand(command="exercise", description="📝 Упражнения (AI)"),
        BotCommand(command='train', description='📝 Тренируем слова'),
        BotCommand(command="ai_status", description="🔍 Статус AI"),
    ]
    await bot.set_my_commands(commands)


