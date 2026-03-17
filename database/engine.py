from aiogram import Bot
from aiogram.types import BufferedInputFile
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from database.crud import (
    orm_add_banner_description,
    orm_change_banner_image,
    orm_create_categories,
    orm_get_info_pages,
)
from database.models import Base
from utils.config import config
from utils.db_texts import categories, info_pages_description
from utils.placeholder import create_placeholder_png

engine = create_async_engine(url=config.database_url, echo=True)
session_maker = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


async def create_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with session_maker() as session:
        await orm_create_categories(session, categories)
        await orm_add_banner_description(session, info_pages_description)


async def seed_banner_images(bot: Bot):
    """Upload a placeholder image to Telegram for all banners that have no image yet.
    Runs once on first startup; subsequent runs are no-ops."""
    async with session_maker() as session:
        banners = await orm_get_info_pages(session)
        missing = [b for b in banners if not b.image]
        if not missing:
            return

        admin_id = config.admins_list[0]
        png = create_placeholder_png()
        msg = await bot.send_photo(
            chat_id=admin_id,
            photo=BufferedInputFile(png, filename='default_banner.png'),
            caption='🖼 Дефолтные баннеры установлены. Замените через /admin → «Добавить/изменить баннер»',
            disable_notification=True,
        )
        file_id = msg.photo[-1].file_id  # type: ignore[index]

        for banner in missing:
            await orm_change_banner_image(session, banner.name, file_id)


async def drop_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
