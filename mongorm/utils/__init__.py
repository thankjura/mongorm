__all__ = ["to_json"]

from typing import Union
from bson import ObjectId


def to_json(obj) -> Union[list, dict, str, int, None]:
    if isinstance(obj, (list, set, tuple)):
        out_list: list = []
        for o in obj:
            out_list.append(to_json(o))

        return out_list

    if hasattr(obj, "__json__"):
        return obj.__json__()

    if isinstance(obj, dict):
        out_dict: dict = {}
        for key, value in obj.items():
            out_dict[key] = to_json(value)

        return out_dict

    if isinstance(obj, ObjectId):
        return str(obj)

    return obj
