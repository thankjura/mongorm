__all__ = ['Datetime']

from datetime import date, datetime
from typing import Optional, Union


from bson import Timestamp

from mongorm.schema.abc_field import AbstractField
from mongorm.exceptions.db.field_exception import FieldValueException


class Datetime(AbstractField):
    def loads(self, value: Union[date, datetime, int, Timestamp, None]) -> Optional[datetime]:
        if value is None:
            return None

        if isinstance(value, datetime):
            return value

        if isinstance(value, date):
            return datetime(value.year, value.month, value.day)

        if isinstance(value, Timestamp):
            return value.as_datetime()

        if isinstance(value, int):
            return datetime.fromtimestamp(value)

        raise FieldValueException('Incorrect format')

    def dumps(self, value: datetime) -> Optional[str]:
        if value:
            return str(value)
