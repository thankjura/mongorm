__all__ = ['BaseDocument']
from typing import Optional

from mongorm.db.connection import Connection
from mongorm.schema import Schema
from mongorm.utils.classproperty import classproperty


class BaseDocument(Schema):
    __collection__ = None

    @classproperty
    def db(self):
        return Connection().db

    @classproperty
    def db_collection(self):
        return self.db[self.__collection__.split(".")[0]]

    @classmethod
    def _wrap_query(cls, query):
        if isinstance(query, dict):
            return {k: cls._wrap_query(v) for k, v in query.items()}
        if isinstance(query, (set, list, tuple)):
            return [cls._wrap_query(v) for v in query]
        return query

    @classmethod
    async def _find(cls, query: dict, sort: Optional[dict], skip: int = 0, limit: int = 0):
        sort = [[k, v] for k, v in sort.items()] if sort else []
        cursor = cls.db_collection.find(query, sort=sort, skip=skip, limit=limit)
        out = []
        async for item in cursor:
            out.append(item)

        return out

    @classmethod
    async def _find_one(cls, query, sort):
        if not sort:
            sort = []
        else:
            sort = [(k, v) for k, v in sort.items()]
        return await cls.db_collection.find_one(query, sort=sort)

    def __init__(self, document=None, extra_fields: dict = None):
        super().__init__(document, extra_fields)
        assert self.__collection__, 'Need set collection name'
