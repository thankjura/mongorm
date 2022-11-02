__all__ = ['AbcSchema']

import abc

from mongorm.schema.meta_schema import MetaSchema


class AbcSchema(metaclass=MetaSchema):
    def __init__(self, *args, **kwargs):
        pass

    @abc.abstractmethod
    def get(self, field_key):
        pass

    @abc.abstractmethod
    def set(self, field_key, value):
        pass

    @abc.abstractmethod
    def _set_data(self, document):
        pass

    @abc.abstractmethod
    def _get_data(self, include: list = None, exclude: list = None):
        pass

    @abc.abstractmethod
    def _get_changes(self, exclude: list = None) -> dict:
        pass

    @abc.abstractmethod
    def has_changes(self):
        pass

    @abc.abstractmethod
    async def validate(self, create=True) -> dict:
        pass

    @abc.abstractmethod
    def load(self, data):
        pass

    @abc.abstractmethod
    def __json__(self):
        pass
