__all__ = ['DocumentField']

import json
from json import JSONDecodeError

from mongorm.schema.abc_schema import AbcSchema
from mongorm.schema.abc_field import AbstractField
from mongorm.exceptions.db.field_exception import FieldValueException


class DocumentField(AbstractField):
    def __init__(self, **kwargs):
        """
        Params:
        :param schema: schema for validation
        """
        super().__init__(**kwargs)
        self.__schema = kwargs.get('schema')
        if self.__schema is not None:
            assert issubclass(self.__schema, AbcSchema)

    @property
    def schema(self):
        return self.__schema

    def __loads(self, value: dict):
        if self.__schema:
            return self.__schema(value)
        return value

    def loads(self, value):
        if value is None and self.__schema:
            if self.__schema:
                return self.__schema()

        if isinstance(value, str):
            try:
                return self.__loads(json.loads(value))
            except JSONDecodeError:
                raise FieldValueException('Incorrect json format')

        if isinstance(value, dict):
            return self.__loads(value)

        if self.__schema and isinstance(value, self.__schema):
            return value

    def dumps(self, value):
        if isinstance(value, dict):
            if self.__schema:
                return self.__schema(value).__json__()
            return {k: v for k, v in value.items()}
        if self.__schema and isinstance(value, self.__schema):
            return value.__json__()
