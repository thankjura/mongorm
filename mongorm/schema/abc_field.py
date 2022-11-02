__all__ = ['AbstractField']

from abc import ABC, abstractmethod
from typing import List

from mongorm.schema.validators import AbstractValidator


class AbstractField(ABC):
    def __init__(self, **kwargs):
        """
        Init params:
        :type no_dumps: bool
        :param no_dumps:
        :type no_loads: bool
        :param no_loads:
        :param default: default value
        :type validators: list
        :param validators: list of validators
        :type display_name: str | Callable
        :param display_name: display name
        """
        self.__default = kwargs.get('default')
        self.__no_dumps = bool(kwargs.get('no_dumps'))
        self.__no_loads = bool(kwargs.get('no_loads'))
        self.__validators = kwargs.get('validators') if kwargs.get('validators') else []
        self.__db_index = kwargs.get('db_index')
        self.__display_name = kwargs.get('display_name')

    @property
    def validators(self) -> List[AbstractValidator]:
        return self.__validators

    @property
    def default(self):
        if self.__default is not None:
            if callable(self.__default):
                return self.__default()
            return self.__default

    @property
    def no_loads(self):
        return self.__no_loads

    @property
    def no_dumps(self):
        return self.__no_dumps

    @property
    def db_index(self):
        return self.__db_index

    @abstractmethod
    def loads(self, value):
        """
        from json object to python object
        :param value:
        :return:
        """
        pass

    @abstractmethod
    def dumps(self, value):
        """
        from python object to json
        :param value:
        :return:
        """
        pass

    @property
    def display_name(self):
        if callable(self.__display_name):
            return self.__display_name()
        return self.__display_name
