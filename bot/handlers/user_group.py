from aiogram import Bot, Router, types
from aiogram.filters import Command
from aiogram.types import BotCommandScopeChat

from bot.filters.custom import ChatTypeFilter
from bot.logging_config import logger
from bot.utils.bot_commands import admin_commands, user_commands

router = Router()
router.message.filter(ChatTypeFilter(chat_types=['group', 'supergroup']))


@router.message(Command('admin'))
async def get_admins(message: types.Message, bot: Bot, admins_list: set[int], owner_id: int):
    if not message.from_user or message.from_user.id != owner_id:
        return

    bot_id = (await message.bot.get_me()).id
    chat_id = message.chat.id
    group_admins = await bot.get_chat_administrators(chat_id)
    new_admins = {
        m.user.id
        for m in group_admins
        if m.status in ('creator', 'administrator')
        if not m.user.id == bot_id
    }
    admins_list.update(new_admins)
    for admin_id in admins_list:
        await message.bot.set_my_commands(
            admin_commands + user_commands,
            scope=BotCommandScopeChat(chat_id=admin_id, user_id=admin_id),
        )
    await message.delete()
    await message.answer(text='Список админов обновлен')
    logger.debug(admins_list)
