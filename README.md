# Telegram Shop Bot

Универсальный Telegram-бот для онлайн-продаж. Подходит для любого бизнеса: кафе, магазин, услуги. Пользователи просматривают каталог по категориям, добавляют товары в корзину и оформляют заказ. Администраторы управляют каталогом и контентом прямо через бот — без сторонних панелей.

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)
![aiogram](https://img.shields.io/badge/aiogram-3.x-2CA5E0?logo=telegram&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?logo=postgresql&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-D71F00)
![uv](https://img.shields.io/badge/uv-package_manager-DE5FE9)

## Возможности

**Для покупателей:**
- Каталог товаров по категориям с пагинацией
- Корзина: добавление, изменение количества, удаление позиций
- Информационные страницы (о компании, оплата, доставка) с изображениями

> **Оплата:** встроенный платёжный модуль не подключён. Логика оплаты реализуется под конкретный проект — Telegram Payments, ЮКасса, ручное подтверждение и т.д.

**Для администраторов:**
- Добавление, редактирование и удаление товаров с фото
- Управление изображениями и описаниями информационных страниц
- Пошаговая FSM-форма для создания товара прямо в чате

**Использование в группах:**
- Бот можно добавить в группу
- Команда `/admin` в группе обновляет список администраторов бота, подтягивая актуальных администраторов чата

## Стек

| Компонент | Технология |
|-----------|------------|
| Бот | [aiogram 3](https://docs.aiogram.dev/) |
| ORM | [SQLAlchemy 2 (async)](https://docs.sqlalchemy.org/) |
| База данных | PostgreSQL 16 |
| Конфигурация | pydantic-settings |
| Логирование | loguru |
| Пакетный менеджер | [uv](https://docs.astral.sh/uv/) |
| Контейнеризация | Docker + docker compose |

## Быстрый старт

### Вариант 1: Docker Compose (рекомендуется)

```bash
git clone <repo-url>
cd tg_shop_bot
cp .env.example .env
# Заполните BOT_TOKEN в .env
docker compose up --build
```

### Вариант 2: uv (локально)

```bash
git clone <repo-url>
cd tg_shop_bot
cp .env.example .env
# Заполните BOT_TOKEN и DATABASE_URL в .env (localhost вместо db)

uv sync
uv run python -m bot
```

### Вариант 3: pip (локально)

```bash
git clone <repo-url>
cd tg_shop_bot
cp .env.example .env
# Заполните BOT_TOKEN и DATABASE_URL в .env

python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install .
python -m bot
```

## Переменные окружения

Скопируйте `.env.example` → `.env` и заполните:

| Переменная | Описание | Пример |
|------------|----------|--------|
| `BOT_TOKEN` | Токен бота от [@BotFather](https://t.me/BotFather) | `123456:ABC-DEF...` |
| `ADMINS_LIST` | Список Telegram user_id администраторов (JSON) | `[123456789]` |
| `DATABASE_URL` | URL подключения к PostgreSQL | `postgresql+asyncpg://user:pass@localhost:5432/shop_db` |
| `POSTGRES_USER` | Пользователь PostgreSQL (для docker-compose) | `user` |
| `POSTGRES_PASSWORD` | Пароль PostgreSQL (для docker-compose) | `password` |
| `POSTGRES_DB` | Имя базы данных (для docker-compose) | `shop_db` |

> При использовании docker-compose `DATABASE_URL` переопределяется автоматически — вручную менять не нужно.

## Структура проекта

```
tg_shop_bot/
├── pyproject.toml
├── Dockerfile
├── docker-compose.yml
├── .env.example
└── bot/
    ├── __main__.py               # Точка входа (python -m bot)
    ├── database/
    │   ├── base.py               # engine, session_maker, Base (created_at/updated_at)
    │   ├── models.py             # SQLAlchemy ORM-модели
    │   ├── crud.py               # CRUD-операции
    │   └── fixture.py            # create_db() / drop_db()
    ├── handlers/
    │   ├── __init__.py           # Сборка всех роутеров в один
    │   ├── admin_private.py      # FSM-форма добавления/редактирования товаров и баннеров
    │   ├── user_private.py       # /start, навигация по inline-меню
    │   ├── menu_processing.py    # Логика уровней меню (0-3)
    │   └── user_group.py         # /admin в группе — синхронизация списка админов
    ├── keyboards/
    │   ├── inline.py             # MenuCallback, inline-кнопки
    │   └── reply.py              # Reply-клавиатуры
    ├── middlewares/
    │   └── db.py                 # Инъекция сессии БД в хэндлеры
    ├── filters/
    │   └── custom.py             # ChatTypeFilter, IsAdmin
    ├── config.py                 # Конфигурация через pydantic-settings
    ├── logging_config.py         # Настройка loguru
    └── utils/
        ├── db_texts.py           # Начальные данные для БД
        ├── paginator.py          # Пагинация
        ├── placeholder.py        # Генерация PNG-заглушек без внешних зависимостей
        └── bot_commands.py       # Команды бота
```
