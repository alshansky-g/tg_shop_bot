from aiogram import Bot, Router, types
from aiogram.filters import Command
from aiogram.types import BotCommandScopeChat

from bot.filters.custom import ChatTypeFilter
from bot.logging_config import logger
from bot.utils.bot_commands import admin_commands, user_commands

router = Router()
router.message.filter(ChatTypeFilter(chat_types=['group', 'supergroup']))


@router.message(Command('admin'))
async def get_admins(message: types.Message, bot: Bot, admins_list: set[int]):
    if message.from_user:
        chat_id = message.chat.id
        admins = await bot.get_chat_administrators(chat_id)
        admins = [
            member.user.id for member in admins if member.status in ('creator', 'administrator')
        ]
        admins_list.update(admins)
        for admin_id in admins_list:
            await message.bot.set_my_commands(
                admin_commands + user_commands,
                scope=BotCommandScopeChat(chat_id=admin_id, user_id=admin_id),
            )
        if message.from_user.id in admins_list:
            await message.delete()
            await message.answer(text='Список админов обновлен')
        logger.debug(admins_list)
