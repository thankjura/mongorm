__all__ = ['Boolean']

from mongorm.schema.abc_field import AbstractField


class Boolean(AbstractField):
    def loads(self, value):
        return True if value else False

    def dumps(self, value):
        if value is not None:
            return bool(value)
        return None
