from aiogram import Bot
from aiogram.types import BufferedInputFile
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from database.crud import (
    orm_add_banner_description,
    orm_change_banner_image,
    orm_create_categories,
    orm_get_info_pages,
    orm_seed_products,
)
from database.models import Base
from utils.config import config
from utils.db_texts import categories, info_pages_description, sample_products
from utils.placeholder import create_placeholder_png

engine = create_async_engine(url=config.database_url, echo=True)
session_maker = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


async def create_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with session_maker() as session:
        await orm_create_categories(session, categories)
        await orm_add_banner_description(session, info_pages_description)


async def seed_initial_data(bot: Bot):
    """Upload a placeholder image and seed banners + demo products on first startup.
    Subsequent runs are no-ops if data already exists."""
    async with session_maker() as session:
        banners = await orm_get_info_pages(session)
        missing_banners = [b for b in banners if not b.image]

        from database.models import Product
        from sqlalchemy import select
        has_products = await session.scalar(select(Product))

        if not missing_banners and has_products is not None:
            return

        admin_id = config.admins_list[0]
        png = create_placeholder_png()
        msg = await bot.send_photo(
            chat_id=admin_id,
            photo=BufferedInputFile(png, filename='default_banner.png'),
            caption='🖼 Стартовые данные загружены. Замените баннеры и товары через /admin.',
            disable_notification=True,
        )
        file_id = msg.photo[-1].file_id  # type: ignore[index]

        for banner in missing_banners:
            await orm_change_banner_image(session, banner.name, file_id)

        await orm_seed_products(session, sample_products, file_id)


async def drop_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
