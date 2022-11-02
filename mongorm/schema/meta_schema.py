from mongorm.db.connection import Connection
from mongorm.schema.abc_field import AbstractField


def get_method(attr_name):
    def __get_method(self):
        return getattr(self, "get")(attr_name)
    return __get_method


def set_method(attr_name):
    def __set_method(self, value):
        return getattr(self, "set")(attr_name, value)
    return __set_method


class MetaSchema(type):
    def __new__(mcs, name, bases, attrs):
        fields: dict[str, AbstractField] = {}

        fields_indexes = []

        for attr in attrs:
            if isinstance(attrs[attr], AbstractField):
                fields[attr] = attrs[attr]
                if attrs[attr].db_index is not None:
                    fields_indexes.append([(attr, attrs[attr].db_index)])

                attrs[attr] = property(get_method(attr), set_method(attr))

        out_class = super(MetaSchema, mcs).__new__(mcs, name, bases, attrs)
        out_class.FIELDS = fields

        if '__collection__' in attrs:
            if '__indexes__' in attrs:
                Connection.create_indexes(attrs['__collection__'], attrs['__indexes__'])
            if fields_indexes:
                Connection.create_indexes(attrs['__collection__'], fields_indexes)

        return out_class
