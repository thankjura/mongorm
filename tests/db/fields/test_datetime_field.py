
from datetime import date, datetime
from bson import Timestamp

from mongorm.db import Document
from mongorm.schema.fields import Datetime


class Model(Document):
    __collection__ = "test_datetime_model"
    datetime = Datetime()


async def test_datetime_field(mongo_db):
    TEST_YEAR = 1961
    TEST_MONTH = 4
    TEST_DAY = 12
    TEST_HOUR = 6
    TEST_MINUTE = 7

    test_date = date(year=TEST_YEAR, month=TEST_MONTH, day=TEST_DAY)
    test_datetime = datetime(year=TEST_YEAR, month=TEST_MONTH, day=TEST_DAY, hour=TEST_HOUR, minute=TEST_MINUTE)

    model = Model({'datetime': test_date})
    await model.save()
    assert isinstance(model.datetime, datetime)
    assert model.datetime.year == TEST_YEAR
    assert model.datetime.month == TEST_MONTH
    assert model.datetime.day == TEST_DAY
    loaded_model = await Model.find_one({'datetime': datetime(year=TEST_YEAR, month=TEST_MONTH, day=TEST_DAY)})
    assert isinstance(loaded_model.datetime, datetime)
    assert loaded_model.datetime.year == TEST_YEAR
    assert loaded_model.datetime.month == TEST_MONTH
    assert loaded_model.datetime.day == TEST_DAY

    model = Model({'datetime': test_datetime})
    await model.save()
    assert isinstance(model.datetime, datetime)
    assert model.datetime.year == TEST_YEAR
    assert model.datetime.month == TEST_MONTH
    assert model.datetime.day == TEST_DAY
    assert model.datetime.hour == TEST_HOUR
    assert model.datetime.minute == TEST_MINUTE
    loaded_model = await Model.find_one({'datetime': datetime(year=TEST_YEAR, month=TEST_MONTH, day=TEST_DAY,
                                                              hour=TEST_HOUR, minute=TEST_MINUTE)})
    assert isinstance(loaded_model.datetime, datetime)
    assert loaded_model.datetime.year == TEST_YEAR
    assert loaded_model.datetime.month == TEST_MONTH
    assert loaded_model.datetime.day == TEST_DAY
    assert loaded_model.datetime.hour == TEST_HOUR
    assert loaded_model.datetime.minute == TEST_MINUTE

    test_timestamp = 1172969203
    test_date = datetime.fromtimestamp(test_timestamp)

    model = Model({'datetime': test_timestamp})
    assert isinstance(model.datetime, datetime)
    await model.save()
    assert isinstance(model.datetime, datetime)
    assert model.datetime.year == test_date.year
    assert model.datetime.month == test_date.month
    assert model.datetime.day == test_date.day
    assert model.datetime.hour == test_date.hour
    assert model.datetime.minute == test_date.minute
    loaded_model = await Model.find_one({'datetime': test_date})
    assert isinstance(loaded_model.datetime, datetime)
    assert loaded_model.datetime.year == test_date.year
    assert loaded_model.datetime.month == test_date.month
    assert loaded_model.datetime.day == test_date.day
    assert loaded_model.datetime.hour == test_date.hour
    assert loaded_model.datetime.minute == test_date.minute

    test_bson_timestamp = Timestamp(1172969203, 1)
    test_datetime = test_bson_timestamp.as_datetime()

    model = Model({'datetime': test_bson_timestamp})
    await model.save()
    assert isinstance(model.datetime, datetime)
    assert model.datetime.year == test_date.year
    assert model.datetime.month == test_datetime.month
    assert model.datetime.day == test_datetime.day
    assert model.datetime.hour == test_datetime.hour
    assert model.datetime.minute == test_datetime.minute
    loaded_model = await Model.find_one({'datetime': test_datetime})
    assert isinstance(loaded_model.datetime, datetime)
    assert loaded_model.datetime.year == test_datetime.year
    assert loaded_model.datetime.month == test_datetime.month
    assert loaded_model.datetime.day == test_datetime.day
    assert loaded_model.datetime.hour == test_datetime.hour
    assert loaded_model.datetime.minute == test_datetime.minute
