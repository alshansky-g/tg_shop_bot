import pytest

from bot.utils.paginator import Paginator


@pytest.fixture
def items():
    return list(range(1, 11))


def test_pages_count(items):
    p = Paginator(items, per_page=3)
    assert p.pages == 4


def test_get_page_first(items):
    p = Paginator(items, page=1, per_page=3)
    assert p.get_page() == [1, 2, 3]


def test_get_page_last(items):
    p = Paginator(items, page=4, per_page=3)
    assert p.get_page() == [10]


def test_has_next_true(items):
    p = Paginator(items, page=1, per_page=3)
    assert p.has_next() == 2


def test_has_next_false_on_last_page(items):
    p = Paginator(items, page=4, per_page=3)
    assert p.has_next() is False


def test_has_previous_true(items):
    p = Paginator(items, page=3, per_page=3)
    assert p.has_previous() == 2


def test_has_previous_false_on_first_page(items):
    p = Paginator(items, page=1, per_page=3)
    assert p.has_previous() is False


def test_get_next_advances_page(items):
    p = Paginator(items, page=1, per_page=3)
    result = p.get_next()
    assert result == [4, 5, 6]
    assert p.page == 2


def test_get_previous_goes_back(items):
    p = Paginator(items, page=3, per_page=3)
    result = p.get_previous()
    assert result == [4, 5, 6]
    assert p.page == 2


def test_get_next_raises_on_last_page(items):
    p = Paginator(items, page=4, per_page=3)
    with pytest.raises(IndexError, match='последняя страница'):
        p.get_next()


def test_get_previous_raises_on_first_page(items):
    p = Paginator(items, page=1, per_page=3)
    with pytest.raises(IndexError, match='первая страница'):
        p.get_previous()


def test_get_buttons_middle_page(items):
    p = Paginator(items, page=2, per_page=3)
    buttons = p.get_buttons()
    assert '◀️ Пред.' in buttons
    assert 'След. ▶️' in buttons


def test_get_buttons_first_page(items):
    p = Paginator(items, page=1, per_page=3)
    buttons = p.get_buttons()
    assert '◀️ Пред.' not in buttons
    assert 'След. ▶️' in buttons


def test_get_buttons_last_page(items):
    p = Paginator(items, page=4, per_page=3)
    buttons = p.get_buttons()
    assert '◀️ Пред.' in buttons
    assert 'След. ▶️' not in buttons


def test_single_page_no_buttons():
    p = Paginator([1, 2], page=1, per_page=5)
    assert p.get_buttons() == {}


def test_works_with_strings():
    p = Paginator(['а', 'б', 'в'], page=1, per_page=2)
    assert p.get_page() == ['а', 'б']
    assert p.pages == 2
