from unittest.mock import MagicMock

import pytest

from bot.filters.custom import ChatTypeFilter, IsAdmin


def make_message(chat_type: str, user_id: int | None = 123):
    message = MagicMock()
    message.chat.type = chat_type
    if user_id is None:
        message.from_user = None
    else:
        message.from_user = MagicMock()
        message.from_user.id = user_id
    return message


# --- ChatTypeFilter ---

@pytest.mark.asyncio
async def test_chat_type_filter_matches():
    f = ChatTypeFilter(chat_types=['private'])
    assert await f(make_message('private')) is True


@pytest.mark.asyncio
async def test_chat_type_filter_no_match():
    f = ChatTypeFilter(chat_types=['group', 'supergroup'])
    assert await f(make_message('private')) is False


@pytest.mark.asyncio
async def test_chat_type_filter_multiple_types():
    f = ChatTypeFilter(chat_types=['group', 'supergroup'])
    assert await f(make_message('group')) is True
    assert await f(make_message('supergroup')) is True


# --- IsAdmin ---

@pytest.mark.asyncio
async def test_is_admin_true():
    f = IsAdmin()
    message = make_message('private', user_id=42)
    assert await f(message, admins_list=[42, 99]) is True


@pytest.mark.asyncio
async def test_is_admin_false():
    f = IsAdmin()
    message = make_message('private', user_id=1)
    assert await f(message, admins_list=[42, 99]) is False


@pytest.mark.asyncio
async def test_is_admin_no_user():
    f = IsAdmin()
    message = make_message('private', user_id=None)
    assert await f(message, admins_list=[42]) is False


@pytest.mark.asyncio
async def test_is_admin_empty_list():
    f = IsAdmin()
    message = make_message('private', user_id=42)
    assert await f(message, admins_list=[]) is False
