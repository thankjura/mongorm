__all__ = ['RefExistsValidator']

from bson import ObjectId
from mongorm.schema.validators.abstract_validator import AbstractValidator


class RefExistsValidator(AbstractValidator):
    def __init__(self, schema, message: str = None, query: dict = None):
        super().__init__(message)
        self.__query = query if query else {}
        self.__schema = schema

    async def is_valid(self, value, field_key: str, model) -> bool:
        if value:
            query = self.__query.copy()
            query['_id'] = ObjectId(value)

            obj = await self.__schema.find_one(query=query)
            if not obj:
                return False
            return True
        return True

    def get_error_message(self) -> str:
        message = super().get_error_message()
        if not message:
            return 'Do not exists'
        return message
