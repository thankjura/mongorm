from tests.db.models.child_schema import ChildSchema, SubChildSchema
from tests.db.models.model import Model


async def test_nested_schema(mongo_db):
    model = Model()
    model.name = "model name"
    await model.save()
    document = ChildSchema({"name": "child_schema"})
    model.document = document
    await model.save()
    assert model.document.name == "child_schema"

    model.document.name = "new name"
    await model.save()
    assert model.document.name == "new name"

    model.document.sub_child = SubChildSchema({"sub_name_one": "name one"})
    await model.save()

    assert model.document.sub_child.sub_name_one == "name one"

    model.document.sub_child.sub_name_one = "new name"
    assert model.document.sub_child.sub_name_one == "new name"
    await model.save()
    assert model.document.sub_child.sub_name_one == "new name"
