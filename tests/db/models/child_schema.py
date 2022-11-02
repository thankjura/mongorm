from gettext import gettext as _
from datetime import datetime

from mongorm.schema import Schema
from mongorm.schema.fields import String, Datetime, DocumentField
from mongorm.schema.validators import RequiredValidator


class SubChildSchema(Schema):
    sub_name_one: str = String()
    sub_name_two: str = String()


class ChildSchema(Schema):
    name: str = String()
    updated: datetime = Datetime(validators=[RequiredValidator(_("required"))], default=datetime.utcnow)
    sub_child: SubChildSchema = DocumentField(schema=SubChildSchema)
