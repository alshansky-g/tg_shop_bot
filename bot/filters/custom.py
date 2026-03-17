"""Module for custom filters."""
from aiogram.filters import Filter
from aiogram.types import Message


class ChatTypeFilter(Filter):
    """Filters different chat scopes."""
    def __init__(self, chat_types: list[str]) -> None:
        self.chat_types = chat_types

    async def __call__(self, message: Message) -> bool:
        return message.chat.type in self.chat_types


class IsAdmin(Filter):
    """Checks if user is admin."""
    async def __call__(self, message: Message, admins_list: list[int]) -> bool:
        if message.from_user:
            return message.from_user.id in admins_list
        return False
