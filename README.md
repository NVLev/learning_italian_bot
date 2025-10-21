# 🇮🇹 Телеграм-бот для изучения итальянского языка

AI-powered интерактивный бот для изучения итальянского языка с поддержкой диалогов, упражнений и персонализированных объяснений через OpenAI API.

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![Aiogram](https://img.shields.io/badge/Aiogram-3.x-blue.svg)](https://docs.aiogram.dev/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue.svg)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)

---

## 🚀 Основные возможности

### 📚 Классическое обучение
- **Тематический словарь** - 10+ тем с итальянской лексикой
- **Интерактивные викторины** - тренировка слов с множественным выбором
- **Идиомы и фразы** - изучение устойчивых выражений
- **Фраза дня** - ежедневная порция знаний

### 🤖 AI-powered функции
- **Объяснение слов через GPT-4** - получи детальное объяснение любого итальянского слова с примерами, синонимами и мнемоническими подсказками
- **Генерация примеров** - создание контекстных предложений с любым словом
- **Практика диалогов** - свободное общение с AI на итальянском с коррекцией ошибок
- **Персонализированные упражнения** - AI генерирует уникальные задания:
  - Fill-in-the-gaps (заполнение пропусков)
  - Quiz с объяснениями
  - Контекстные задачи

### 🛠 Технические особенности
- Асинхронная работа с PostgreSQL через SQLAlchemy 2.0
- Контейнеризация через Docker Compose
- Автоматические миграции БД (Alembic)
- Graceful degradation (AI функции работают опционально)
- FSM для управления диалоговыми состояниями

---

## 📦 Технологический стек

**Backend:**
- Python 3.11+
- Aiogram 3.x (async Telegram bot framework)
- SQLAlchemy 2.0 (async ORM)
- Alembic (database migrations)
- Pydantic & Pydantic Settings (configuration)

**AI/ML:**
- OpenAI API (GPT-4o) для диалогов и генерации контента
- Custom conversation management с историей контекста

**Database:**
- PostgreSQL 16+
- Async connection pooling

**DevOps:**
- Docker & Docker Compose
- Poetry для управления зависимостями
- Structured logging

---

## 🏗 Архитектура проекта

```
learning_italian_bot/
├── admin/                      # Handlers 
│   ├── advanced_handlers.py    # AI dialogs and exercises
│   ├── ai_handlers.py          # AI explanations and examples
│   ├── quiz_handlers.py        # Quiz
│   ├── handlers.py             # Basic handlers
│   └── start_handlers.py       # Starting commands
│
├── services/                   # Business logic layer
│   ├── admin_functions.py      # Formatting and help message
│   ├── openai_service.py       # OpenAI API integration
│   ├── conversation_service.py # Managing dialogs (AI)
│   ├── user_service.py         # Manging users and user progress
│   └── exercise_service.py     # Exercise generation (AI)
│
├── database/                   # Data access layer
│   ├── db_helper.py            # Async session management 
│   ├── functions.py            # Database operations
│   └── db_main.py              # Data import scripts
│
├── model/                      # SQLAlchemy models
│   └── model.py                # Theme, Vocabulary, Idiom
│
├── db_config/                  # Configuration
│   └── db_config.py            # Pydantic Settings
│
├── filters/
│   └── filter.py               # Theme filter
│
├── inline_keyboard/
│   └── inline_kb_w_call_back.py # Inline keyboards
│
├── reply_keyboard/             # UI components
│   └── rep_kb.py               # Keyboard builders
│
├── middleware/                 # Aiogram middlewares
│   └── middleware.py           # Database session injection
│
├── migration/                  # Alembic migrations
│   └── versions/
│
└── utils/                      # Utilities
    ├── set_commands.py         # Bot menu setup
    └── states.py               # FSM states
```

---

## ⚙️ Установка и запуск

### Вариант 1: Docker (рекомендуется)

1. **Клонируйте репозиторий:**
```bash
git clone https://github.com/NVLev/learning_italian_bot.git
cd learning_italian_bot
```

2. **Создайте `.env` файл:**
```bash
# Telegram Bot
BOT__TOKEN=your_telegram_bot_token
BOT__ADMIN_IDS=[]

# Database
DB__URL=postgresql+asyncpg://user:password@pg:5432/learning_language
DB__ECHO=false
DB__POOL_SIZE=10

# OpenAI (опционально)
OPENAI__API_KEY=sk-your-openai-key
OPENAI__ENABLED=true
OPENAI__MODEL=gpt-4o
```

3. **Запустите через Docker:**
```bash
docker-compose up --build
```

Бот автоматически:
- Применит миграции БД
- Импортирует начальные данные (словари, идиомы)
- Запустится и будет готов к работе

---

### Вариант 2: Локальная установка

1. **Установите зависимости:**
```bash
poetry install
# или
pip install -r requirements.txt
```

2. **Настройте PostgreSQL:**
```bash
# Создайте БД
createdb learning_language
```

3. **Примените миграции:**
```bash
alembic upgrade head
```

4. **Импортируйте данные:**
```bash
python -m database.db_main
```

5. **Запустите бота:**
```bash
python main.py
```

---

## 🎮 Использование

### Основные команды

- `/start` - Запуск бота и главное меню
- `/help` - Справка по командам
- `/learn` - Изучение слов по темам
- `/train` - Тренировка с викторинами

### AI-команды

- `/explain <слово>` - Получить детальное объяснение слова от AI
- `/example <слово>` - Сгенерировать пример предложения
- `/conversation` - Начать практику диалога с AI
- `/exercise` - Получить персонализированное упражнение
- `/ai_status` - Проверить статус AI-сервиса

### Примеры использования

**Объяснение слова:**
```
Ты: /explain amore
Бот: 🤖 Объяснение слова 'amore'

📖 Перевод: любовь

Примеры:
1. Ti amo con tutto il cuore | Я люблю тебя всем сердцем
2. L'amore vince sempre | Любовь всегда побеждает

💡 Мнемоника: "Amore" похоже на "амур" - бог любви!
```

**Практика диалога:**
```
Бот: Ciao! Come stai oggi?
Ты: Io sto bene, grazie
Бот: Perfetto! Cosa hai fatto oggi?
     ✅ Отлично построено предложение!
```

---

## 🧪 Разработка

### Создание новой миграции

```bash
# Локально
alembic revision --autogenerate -m "add new table"

# В Docker
docker-compose exec bot alembic revision --autogenerate -m "add new table"
```

### Применение миграций

```bash
# Локально
alembic upgrade head

# В Docker (автоматически при запуске)
docker-compose up
```

### Запуск тестов

```bash
# TODO: Добавить тесты
pytest tests/
```

---

## 📊 Структура базы данных

```sql
-- Темы словаря
CREATE TABLE themes (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) UNIQUE NOT NULL
);

-- Словарь (слова по темам)
CREATE TABLE vocabulary (
    id SERIAL PRIMARY KEY,
    italian_word VARCHAR(50) NOT NULL,
    rus_word VARCHAR(50) NOT NULL,
    theme_id INTEGER REFERENCES themes(id)
);

-- Идиомы
CREATE TABLE idiom (
    id SERIAL PRIMARY KEY,
    italian_idiom TEXT NOT NULL,
    rus_idiom TEXT NOT NULL
);
```

---

## 🔒 Безопасность

- API ключи хранятся в переменных окружения
- PostgreSQL с аутентификацией
- Graceful shutdown для корректной остановки
- Rate limiting для OpenAI запросов (planned)

---

## 🚧 Roadmap

### В разработке
- [ ] Система прогресса пользователя (статистика, streak)
- [ ] Spaced repetition алгоритм (SM-2)
- [ ] Расширенная аналитика обучения
- [ ] Голосовые функции (TTS/STT)

### Планируется
- [ ] Unit & Integration тесты (pytest)
- [ ] CI/CD pipeline (GitHub Actions)
- [ ] Admin веб-панель (FastAPI + React)
- [ ] Система достижений и геймификация
- [ ] Таблица лидеров

---

## 🤝 Вклад в проект

Проект открыт для улучшений! Если хочешь добавить функционал:

1. Fork репозитория
2. Создай feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit изменения (`git commit -m 'Add some AmazingFeature'`)
4. Push в branch (`git push origin feature/AmazingFeature`)
5. Открой Pull Request

---

## 📝 Лицензия

Этот проект распространяется под лицензией MIT. См. файл `LICENSE` для деталей.

---

## 👩‍💻 Автор

**Наталья Левант**

- GitHub: [@NVLev](https://github.com/NVLev)
- Telegram: [@VladislavnaSpb](https://t.me/VladislavnaSpb)
- Email: an_smir@mail.ru

---

