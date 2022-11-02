from mongorm.db import Document
from mongorm.schema.fields import String


TEXT_LAT = """
Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et
dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip 
ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu 
fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt 
mollit anim id est laborum.
"""

TEXT_RUS = """
Тьма, пришедшая со Средиземного моря, накрыла ненавидимый прокуратором город. 
Исчезли висячие мосты, соединяющие храм со страшной Антониевой башней, опустилась с неба бездна и залила 
крылатых богов над гипподромом, Хасмонейский дворец с бойницами, базары, караван-сараи, переулки, пруды...
Пропал Ершалаим – великий город, как будто не существовал на свете. 
Всё пожрала тьма, напугавшая все живое в Ершалаиме и его окрестностях.
"""


class Model(Document):
    __collection__ = "test_string_model"
    string = String()


async def test_string_field(mongo_db):
    model = Model({'string': TEXT_LAT})
    await model.save()
    assert model.string == TEXT_LAT
    loaded_model = await Model.find_one({'string': TEXT_LAT})
    assert loaded_model.string == TEXT_LAT

    model = Model({'string': TEXT_RUS})
    await model.save()
    assert model.string == TEXT_RUS
    loaded_model = await Model.find_one({'string': TEXT_RUS})
    assert loaded_model.string == TEXT_RUS

    model = Model({'string': 42})
    await model.save()
    assert model.string == '42'
    loaded_model = await Model.find_one({'string': '42'})
    assert loaded_model.string == '42'

    model = Model({'string': ''})
    await model.save()
    assert model.string is None
    loaded_model = await Model.find_one({'string': None})
    assert loaded_model.string is None
