# Телеграм бот для изучения итальянского языка

## Стек технологий:
- Aiogram
- PostgreSQL
- SQLAlchemy
- Poetry
- BeautifulSoup4
- Docker

## Запуск бота:
1. Скачайте репозиторий:
    ```bash
    git clone https://github.com/NVLev/learning_italian_bot.git
    cd learning_italian_bot
    ```
2. Создайте файл `.env` по шаблону:
    ```env
    BOT_TOKEN=your_telegram_bot_token
    DATABASE_URL=your_database_url
    ```
3. Запустите бота командой:
    ```bash
    docker-compose up --build -d
    ```

## Функциональность:
- Изучение лексики:
  - Получение списка слов по темам
  - Тренировка слов
- Парсинг страниц с помощью BeautifulSoup4 и добавление полученных слов в базу данных


