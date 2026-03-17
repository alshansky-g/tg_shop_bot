from string import punctuation

from aiogram import Bot, Router, types
from aiogram.filters import Command

from bot.filters.custom import ChatTypeFilter
from bot.utils.logging_config import logger

router = Router()
router.message.filter(ChatTypeFilter(chat_types=['group', 'supergroup']))

restricted_words = {'кабан', 'хомяк', 'выхухоль'}


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


def clean_text(text: str):
    return text.translate(str.maketrans('', '', punctuation))


@router.edited_message()
@router.message()
async def cleaner(message: types.Message):
    if message.text and message.from_user:
        if restricted_words.intersection(clean_text(message.text.lower()).split()):
            await message.reply(
                text=f'{message.from_user.first_name}, '
                'запрещено использовать оскорбления. Вас предупредили.'
            )
            await message.delete()
            # await message.chat.ban(message.from_user.id)
        else:
            await message.answer(message.text)
