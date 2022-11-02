__all__ = ['Integer']

from mongorm.schema.abc_field import AbstractField
from mongorm.exceptions.db.field_exception import FieldValueException


class Integer(AbstractField):
    def loads(self, value):
        if value is not None:
            try:
                return int(value)
            except ValueError:
                raise FieldValueException('Incorrect format')

        return None

    def dumps(self, value):
        return value
