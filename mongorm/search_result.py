from typing import Union

from mongorm.utils import to_json


class SearchResult:
    def __init__(self, items: list, name: str = 'items', **kwargs):
        """
        :param items: collection of return objects
        :param name: name of return collection
        :param int total: total of objects, default if items count
        :param int limit: page size
        :param int page: current page
        """
        self.__items = items
        self.__name = name
        self.__total = kwargs['total'] if kwargs.get('total') else len(items)
        self.__limit = kwargs['limit'] if kwargs.get('limit') is not None else len(items)
        self.__page = kwargs['page'] if kwargs.get('page') else 1

    @property
    def limit(self):
        return self.__limit

    @limit.setter
    def limit(self, limit: int):
        if not limit or limit < 1:
            limit = 1
        self.__limit = limit

    @property
    def total(self):
        return self.__total

    @total.setter
    def total(self, total: int):
        self.__total = total

    @property
    def page(self):
        return self.__page

    @page.setter
    def page(self, page):
        self.__page = page

    @property
    def items(self):
        return self.__items

    @items.setter
    def items(self, items):
        self.__items = items

    def __json__(self) -> Union[list, dict]:
        out: dict = {
            "limit": self.limit,
            "total": self.total,
            "page": self.page,
            self.__name: [to_json(obj) for obj in self.items]
        }

        return out
