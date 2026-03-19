import asyncio

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommandScopeChat

from bot.config import config
from bot.database.base import session_maker
from bot.database.fixture import create_db  # , drop_db
from bot.handlers import router
from bot.logging_config import logger
from bot.middlewares.db import DataBaseSession
from bot.utils.bot_commands import admin_commands, user_commands

bot = Bot(token=config.bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

dp = Dispatcher()
dp.update.middleware(DataBaseSession(session_maker))
dp.include_router(router)


async def on_startup():
    await create_db()
    await bot.set_my_commands(user_commands)
    for admin_id in config.admins_list:
        await bot.set_my_commands(
            admin_commands + user_commands,
            scope=BotCommandScopeChat(user_id=admin_id, chat_id=admin_id),
        )


async def on_shutdown():
    # await drop_db()
    # logger.debug('БД удалена')

    for admin_id in config.admins_list:
        await bot.delete_my_commands(
            scope=BotCommandScopeChat(user_id=admin_id, chat_id=admin_id),
        )
        logger.debug(f'Админ клавиатура для {admin_id} удалена.')

    logger.debug('Бот остановлен')


async def main():
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(
        bot,
        allowed_updates=dp.resolve_used_update_types(),
        admins_list=config.admins_list,
        payment_token=config.payment_token,
    )


if __name__ == '__main__':
    asyncio.run(main())
