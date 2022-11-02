from bson import ObjectId

from tests.db.models.child_model import ChildModel
from tests.db.models.model import Model


DEFAULT = "DEFAULT"
MODEL_NAME = "model name"


async def test_crud_model(mongo_db):
    model = Model()
    model.name = MODEL_NAME
    await model.save()
    assert isinstance(model._id, ObjectId)
    assert model.name == MODEL_NAME
    same_model = await Model.get_by_id(model._id)
    assert isinstance(same_model, Model)
    assert same_model._id == model._id
    same_model = await Model.find_one({"name": model.name})
    assert same_model.name == model.name
    await same_model.delete()

    same_model = await Model.get_by_id(model._id)
    assert same_model is None


CHILD = "child"
CHILD1 = "child1"
CHILD2 = "child2"


async def test_nested_model(mongo_db):
    model = Model({"name": "new model"})
    await model.save()
    assert isinstance(model._id, ObjectId)

    child = ChildModel(parent_id=model._id, document={"name": CHILD})
    await child.save()
    assert child._id is not None
    child.load({"name": CHILD1})
    await child.save()
    assert child._id is not None
    child_id: ObjectId = child._id
    assert isinstance(child_id, ObjectId)
    assert child.name == CHILD1
    child.name = CHILD2
    assert child.name == CHILD2
    await child.save()
    assert child_id == child._id
    children = await ChildModel.find({}, parent_id=model.get("_id"))
    assert len(children) == 1
    await child.delete()
    children = await ChildModel.find({}, parent_id=model.get("_id"))
    assert len(children) == 0
