from bson import ObjectId

from mongorm.schema import Schema, fields


class MySchema(Schema):
    id_field: str = fields.ObjectIdField()
    string_field: str = fields.String()
    float_field: float = fields.Float()
    integer_field: float = fields.Integer()
    datetime_field: float = fields.Datetime()
    bool_field: float = fields.Boolean()


def test_simple_schema():
    id_value = ObjectId()
    string_value = 'string_value'
    schema = MySchema({'id_field': id_value})
    assert schema.id_field == id_value
    schema.string_field = string_value
    assert schema.string_field == string_value
    assert schema.has_changes()
    schema = MySchema(schema.__json__())
    assert not schema.has_changes()
