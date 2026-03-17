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
uv run python app.py
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
python app.py
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

> При использовании docker-compose в `DATABASE_URL` укажите `@db:5432` вместо `@localhost:5432`

## Структура проекта

```
tg_shop_bot/
├── app.py                    # Точка входа
├── pyproject.toml            # Зависимости (uv/pip)
├── Dockerfile
├── docker-compose.yml
├── .env.example
├── database/
│   ├── models.py             # SQLAlchemy ORM-модели
│   ├── engine.py             # Подключение к БД, инициализация
│   └── crud.py               # CRUD-операции
├── handlers/
│   ├── admin_private.py      # Управление товарами и баннерами
│   ├── user_private.py       # Старт, главное меню
│   ├── menu_processing.py    # Логика навигации по меню
│   └── user_group.py         # Модерация в группах
├── keyboards/
│   ├── inline.py             # Inline-кнопки (MenuCallback)
│   └── reply.py              # Reply-клавиатуры
├── middlewares/
│   └── db.py                 # Инъекция сессии БД
├── filters/
│   └── custom.py             # Фильтры (тип чата, роль админа)
└── utils/
    ├── config.py             # Конфигурация через pydantic-settings
    ├── db_texts.py           # Начальные данные для БД (категории, страницы)
    ├── logging_config.py     # Настройка loguru
    ├── paginator.py          # Пагинация товаров
    └── bot_commands.py       # Команды бота
```
