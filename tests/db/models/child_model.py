from bson import ObjectId

from mongorm.db.document import NestedDocument
from mongorm.schema.fields import ObjectIdField, String


class ChildModel(NestedDocument):
    __collection__ = "models.children"

    _id: ObjectId = ObjectIdField(no_loads=True, default=ObjectId)
    name: str = String()
