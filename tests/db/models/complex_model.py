from datetime import datetime

from bson import ObjectId

from mongorm.db import Document
from mongorm.schema import Schema
from mongorm.schema.fields import Integer, ObjectIdField, String, DocumentField, Datetime


class NestedNestedDocument(Schema):
    a: str = String(default='')
    b: int = Integer(default=0)


class NestedDocument(Schema):
    nested_string_field: str = String(default='')
    nested_integer_field: int = Integer(default=0)
    nested_datetime_field: datetime = Datetime(default=datetime.utcnow)
    nested_document_field: NestedNestedDocument = DocumentField(schema=NestedNestedDocument)


class ComplexModel(Document):
    __collection__ = "complexModels"

    _id: ObjectId = ObjectIdField(no_loads=True)
    string_field: str = String(default='')
    integer_field: int = Integer(default=0)
    datetime_field: datetime = Datetime(default=datetime.utcnow)
    document_field: NestedDocument = DocumentField(schema=NestedDocument)
