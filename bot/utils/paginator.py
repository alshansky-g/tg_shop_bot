from collections.abc import Sequence
from math import ceil


class Paginator:
    def __init__(
        self, array: Sequence, page: int = 1, per_page: int = 1
    ):
        self.array = array
        self.page = page
        self.per_page = per_page
        self.len = len(array)
        self.pages = ceil(self.len / self.per_page)

    def _get_slice(self):
        start = (self.page - 1) * self.per_page
        stop = start + self.per_page
        return self.array[start:stop]

    def get_page(self):
        page_items = self._get_slice()
        return page_items

    def get_buttons(self):
        buttons = dict()
        if self.has_previous():
            buttons['◀️ Пред.'] = 'previous'
        if self.has_next():
            buttons['След. ▶️'] = 'next'
        return buttons

    def has_next(self):
        if self.page < self.pages:
            return self.page + 1
        return False

    def has_previous(self):
        if self.page > 1:
            return self.page - 1
        return False

    def get_next(self):
        if self.page < self.pages:
            self.page += 1
            return self.get_page()
        raise IndexError('Это последняя страница')

    def get_previous(self):
        if self.page > 1:
            self.page -= 1
            return self._get_slice()
        raise IndexError('Это первая страница')
