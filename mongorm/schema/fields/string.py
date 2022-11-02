__all__ = ['String']

from mongorm.schema.abc_field import AbstractField


class String(AbstractField):
    def loads(self, value):
        return str(value) if value else None

    def dumps(self, value):
        return str(value) if value else None
