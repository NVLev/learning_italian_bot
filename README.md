# Телеграм бот для изучения итальянского языка
 
Проект создан на базе **Aiogram** и использует базы данных, парсинг словарей и интерактивные викторины для улучшения запоминания слов и фраз.

---

## 🚀 Возможности

- Обучение итальянскому языку через интерактивные упражнения  
- Викторины и тесты для закрепления материала  
- Работа с пользовательскими данными и прогрессом  
- Использование inline и reply клавиатур  
- Админ-панель для управления контентом  
- Поддержка Docker и Alembic миграций

---

## 🧩 Структура проекта

```
learning_italian_bot/
├── Dockerfile
├── docker-compose.yaml
├── pyproject.toml
├── requirements.txt
├── alembic.ini
├── loader.py
├── main.py
├── commands.txt
│
├── admin/
│   ├── db_handler.py
│   ├── handlers.py
│   ├── quiz_handlers.py
│   └── start_handlers.py
│
├── api/
│   ├── parser_phrase.py
│   └── parser_vocabulary.py
│
├── config_data/
│   └── config.py
│
├── database/
│   ├── db_helper.py
│   ├── db_main.py
│   ├── functions.py
│   ├── italian_idioms.json
│   └── vocabulary.json
│
├── db_config/
│   └── db_config.py
│
├── filters/
│   └── filter.py
│
├── functions_for_handler/
│   └── admin_functions.py
│
├── inline_keyboard/
│   └── inline_kb_w_call_back.py
│
├── middleware/
│   └── middleware.py
│
├── migration/
│   ├── env.py
│   └── script.py.mako
│
├── model/
│   └── model.py
│
├── reply_keyboard/
│   └── rep_kb.py
│
├── schemas/
│   └── schemas.py
│
└── utils/
    ├── set_commands.py
    └── states.py
```

---

## ⚙️ Установка и запуск

### 1. Клонирование репозитория
```bash
git clone https://github.com/NVLev/learning_italian_bot.git
cd learning_italian_bot
```

### 2. Создание `.env` файла
Добавьте переменные окружения (пример):
```
BOT_TOKEN=your_telegram_bot_token
DATABASE_URL=postgresql://user:password@db:5432/italian_bot
```

### 3. Установка зависимостей

#### Через Poetry:
```bash
poetry install
```

#### Или через pip:
```bash
pip install -r requirements.txt
```

### 4. Миграции базы данных
```bash
alembic upgrade head
```

### 5. Запуск
```bash
python main.py
```

---

## 🐳 Запуск через Docker

```bash
docker-compose up --build
```

---

## 🧠 Технологии

- Python 3.11+
- Aiogram
- SQLAlchemy
- Alembic
- Pydantic
- Docker
- PostgreSQL

---

## 📂 Структура FSM и хендлеров

FSM используется для пошагового взаимодействия пользователя с ботом.  
Все состояния определены в `utils/states.py`, а логика — в соответствующих хендлерах модулей `admin/`, `functions_for_handler/`, и т.д.

---

## 📋 TODO / Возможные улучшения

- Добавить веб-интерфейс для админки  
- Логирование и аналитика ответов пользователей  
- Тесты для ключевых модулей  
- Расширение словаря и парсинг новых источников

---

## 🧑‍💻 Автор

**NVLev**  
📫 Telegram: [@NVLev](https://t.me/NVLev)

---


