__all__ = ['UniqueValidator']

from bson import ObjectId
from mongorm.schema.validators.abstract_validator import AbstractValidator


class UniqueValidator(AbstractValidator):
    def __init__(self, error_message=None):
        if not error_message:
            error_message = 'Already exists'
        super().__init__(error_message)

    async def is_valid(self, value, field_key: str, model) -> bool:
        if value:
            query = {
                field_key: value
            }
            if model.get('_id'):
                query['_id'] = {'$ne': ObjectId(model.get('_id'))}

            obj = await model.find_one(query=query)
            if not obj:
                return True
            return False
        return True
