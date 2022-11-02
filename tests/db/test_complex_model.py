from datetime import datetime


from tests.db.models.complex_model import ComplexModel, NestedDocument, NestedNestedDocument


STRING_VALUE = 'string value'
INTEGER_VALUE = 2128506


async def test_complex_model(mongo_db):
    complex_model = ComplexModel({
        "string_field": STRING_VALUE,
        "integer_field": INTEGER_VALUE,
        "document_field": NestedDocument({
            "nested_string_field": STRING_VALUE,
            "nested_integer_field": INTEGER_VALUE,
            "nested_document_field": NestedNestedDocument({
                "a": STRING_VALUE,
                "b": INTEGER_VALUE
            })
        })
    })
    await complex_model.save()
    assert complex_model._id is not None

    model_oid = complex_model._id
    same_complex_model = await ComplexModel.get_by_id(model_oid)

    assert same_complex_model
    assert same_complex_model.string_field == STRING_VALUE
    assert same_complex_model.integer_field == INTEGER_VALUE
    assert isinstance(same_complex_model.datetime_field, datetime)

    assert same_complex_model.document_field.nested_string_field == STRING_VALUE
    assert same_complex_model.document_field.nested_integer_field == INTEGER_VALUE
    assert isinstance(same_complex_model.document_field.nested_datetime_field, datetime)

    assert same_complex_model.document_field.nested_document_field.a == STRING_VALUE
    assert same_complex_model.document_field.nested_document_field.b == INTEGER_VALUE


async def test_complex_model_with_load(mongo_db):
    complex_model = ComplexModel().load({
        "string_field": STRING_VALUE,
        "integer_field": INTEGER_VALUE,
        "document_field": NestedDocument({
            "nested_string_field": STRING_VALUE,
            "nested_integer_field": INTEGER_VALUE,
            "nested_document_field": NestedNestedDocument({
                "a": STRING_VALUE,
                "b": INTEGER_VALUE
            })
        })
    })
    await complex_model.save()
    assert complex_model._id is not None

    model_oid = complex_model._id
    same_complex_model = await ComplexModel.get_by_id(model_oid)

    assert same_complex_model
    assert same_complex_model.string_field == STRING_VALUE
    assert same_complex_model.integer_field == INTEGER_VALUE
    assert isinstance(same_complex_model.datetime_field, datetime)

    assert same_complex_model.document_field.nested_string_field == STRING_VALUE
    assert same_complex_model.document_field.nested_integer_field == INTEGER_VALUE
    assert isinstance(same_complex_model.document_field.nested_datetime_field, datetime)

    assert same_complex_model.document_field.nested_document_field.a == STRING_VALUE
    assert same_complex_model.document_field.nested_document_field.b == INTEGER_VALUE
