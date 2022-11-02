from typing import List

from bson import ObjectId

from mongorm.db import Document
from mongorm.schema.fields import ObjectIdField, String, Collection, DocumentField
from .child_model import ChildModel
from .child_schema import ChildSchema


class AnotherModel(Document):
    __collection__ = "another_models"

    _id: ObjectId = ObjectIdField(no_loads=True)
    name: str = String()


class Model(Document):
    __collection__ = "models"

    _id: ObjectId = ObjectIdField(no_loads=True)
    name: str = String()
    description: str = String()
    children: List[ChildModel] = Collection(doc_type=ChildModel)
    document: ChildSchema = DocumentField(schema=ChildSchema)
    custom_document = DocumentField()
    another_document_id = ObjectIdField(ref=AnotherModel)

