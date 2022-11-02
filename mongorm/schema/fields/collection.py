__all__ = ['Collection']

from mongorm.schema.abc_field import AbstractField
from mongorm.schema.abc_schema import AbcSchema
from mongorm.utils import to_json


class Collection(AbstractField):
    def __init__(self, doc_type=None, **kwargs):
        """
        Params:
        :param doc_type: type of list item
        """
        super().__init__(**kwargs)
        self.__doc_type: AbstractField = doc_type

    @property
    def doc_type(self):
        return self.__doc_type

    def loads(self, value):
        if isinstance(value, (list, set, type)):
            out = []
            if not self.__doc_type:
                return [v for v in value]

            for i in value:
                if isinstance(self.__doc_type, AbstractField):
                    v = self.__doc_type.loads(i)
                elif issubclass(self.__doc_type, AbcSchema):
                    v = self.__doc_type(i)
                else:
                    v = value
                if v:
                    out.append(v)

            return out

        return []

    def dumps(self, value):
        if isinstance(value, (list, tuple, set)):
            out = []
            for v in value:
                if v is not None:
                    out.append(to_json(v))

            return out

        return value
