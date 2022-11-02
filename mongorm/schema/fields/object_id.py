__all__ = ['ObjectIdField']

from bson import ObjectId
from mongorm.schema.abc_field import AbstractField
from mongorm.schema.validators import RefExistsValidator
from mongorm.schema.abc_schema import AbcSchema
from mongorm.exceptions.db.field_exception import FieldValueException


class ObjectIdField(AbstractField):
    def __init__(self, ref=None, **kwargs):
        super().__init__(**kwargs)
        self.__ref = ref
        if self.__ref:
            self.validators.append(RefExistsValidator(self.__ref))

    @property
    def ref(self):
        return self.__ref

    def loads(self, value):
        if not value:
            return None

        if isinstance(value, ObjectId):
            return value

        if isinstance(value, AbcSchema):
            if (self.__ref and isinstance(value, self.__ref)) or not self.__ref:
                return self.loads(value.get('_id'))

        try:
            return ObjectId(value)
        except ValueError:
            return FieldValueException()

    def dumps(self, value):
        if value:
            return str(value)
