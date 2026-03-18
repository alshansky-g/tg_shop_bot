from aiogram import Bot, Router, types
from aiogram.filters import Command

from bot.filters.custom import ChatTypeFilter
from bot.utils.logging_config import logger

router = Router()
router.message.filter(ChatTypeFilter(chat_types=['group', 'supergroup']))


@router.message(Command('admin'))
async def get_admins(message: types.Message, bot: Bot, admins_list: list[int]):
    if message.from_user:
        chat_id = message.chat.id
        admins = await bot.get_chat_administrators(chat_id)
        admins = [
            member.user.id for member in admins if member.status in ('creator', 'administrator')
        ]
        admins_list = admins
        if message.from_user.id in admins_list:
            await message.delete()
        logger.debug(admins_list)
