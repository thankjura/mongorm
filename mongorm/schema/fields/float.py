__all__ = ['Float']

from mongorm.schema.abc_field import AbstractField
from mongorm.exceptions.db.field_exception import FieldValueException


class Float(AbstractField):
    def loads(self, value):
        if value is not None and value != '':
            try:
                return float(value)
            except ValueError:
                raise FieldValueException('Incorrect format')

        return None

    def dumps(self, value):
        return value
