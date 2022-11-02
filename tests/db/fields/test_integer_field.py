import sys

import pytest

from mongorm.db import Document
from mongorm.exceptions.db.field_exception import FieldValueException
from mongorm.schema.fields import Integer


class Model(Document):
    __collection__ = "test_integer_model"
    integer = Integer()


async def test_integer_field(mongo_db):
    model = Model({'integer': 42})
    await model.save()
    assert model.integer == 42
    loaded_model = await Model.find_one({'integer': 42})
    assert loaded_model.integer == 42

    model = Model({'integer': '2128506'})
    await model.save()
    assert model.integer == 2128506
    loaded_model = await Model.find_one({'integer': 2128506})
    assert loaded_model.integer == 2128506

    model = Model({'integer': sys.maxsize})
    await model.save()
    assert model.integer == sys.maxsize
    loaded_model = await Model.find_one({'integer': sys.maxsize})
    assert loaded_model.integer == sys.maxsize

    model = Model({'integer': -sys.maxsize})
    await model.save()
    assert model.integer == -sys.maxsize
    loaded_model = await Model.find_one({'integer': -sys.maxsize})
    assert loaded_model.integer == -sys.maxsize

    model = Model({'integer': None})
    await model.save()
    assert model.integer is None
    loaded_model = await Model.find_one({'integer': None})
    assert loaded_model.integer is None

    with pytest.raises(FieldValueException):
        model = Model({'integer': ''})
        await model.save()
