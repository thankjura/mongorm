__all__ = ['MapField']

import json
from json import JSONDecodeError

from mongorm.schema.abc_field import AbstractField
from mongorm.exceptions.db.field_exception import FieldValueException


class MapField(AbstractField):
    def __init__(self, value_type: AbstractField, **kwargs):
        """
        Params:
        :type value_type: AbstractField
        :param value_type: value type
        """
        super().__init__(**kwargs)
        self.__value_type: AbstractField = value_type

    @property
    def value_type(self):
        return self.__value_type

    def __loads(self, value: dict):
        return {str(k): self.__value_type.loads(v) for k, v in value.items()}

    def loads(self, value):
        if value is None:
            return None

        if isinstance(value, str):
            try:
                return self.__loads(json.loads(value))
            except JSONDecodeError:
                raise FieldValueException('Incorrect json format')

        if isinstance(value, dict):
            return self.__loads(value)

    def dumps(self, value):
        if isinstance(value, dict):
            return {str(k): self.__value_type.dumps(v) for k, v in value.items()}
