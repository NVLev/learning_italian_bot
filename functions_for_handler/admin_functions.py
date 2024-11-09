from aiogram.types import InputFile, ReplyKeyboardRemove, Message



def format_word_list(words):
    # Header
    message = "️📚 Italian │ Russian\n"
    message += "━━━━━━━━━━━━━━━━━━━\n"

    # Words
    for word in words:
        message += f"{word.italian_word.ljust(20)} │ {word.rus_word}\n"

    return message



def help_message() -> str:
    return ('Этот бот поможет вам изучить лексику итальянского языка.'
            'Можете посмотреть слова по темам, нажав 📖 Изучаем слова.'
            'Если хотите проверить знания, нажмите 📝 Тренируем слова.'
            'А можно просто нажать 📚 Фраза дня, и посмотреть, что за идиома вам выпадет сегодня')


async def help_command(message: Message):
    await message.answer(help_message())