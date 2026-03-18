from bot.database.base import engine, session_maker
from bot.database.crud import orm_add_banner_description, orm_create_categories, orm_seed_products
from bot.database.models import Base
from bot.utils.db_texts import categories, info_pages_description, sample_products


async def create_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with session_maker() as session:
        await orm_create_categories(session, categories)
        await orm_add_banner_description(session, info_pages_description)
        await orm_seed_products(session, sample_products, placeholder_image='placeholder')


async def drop_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
