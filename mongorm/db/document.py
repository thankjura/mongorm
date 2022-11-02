__all__ = ['Document', 'NestedDocument']

from typing import Dict, Optional, Type, List, TypeVar, Union

import pymongo
from bson import ObjectId

from mongorm.db.base import BaseDocument
from mongorm.schema import fields
from mongorm.exceptions.validation_error import ValidationError
from mongorm.search_result import SearchResult
from mongorm.utils.classproperty import classproperty

D = TypeVar('D', bound='Document')
ND = TypeVar('ND', bound='NestedDocument')

DEFAULT_LIMIT = 20
DEFAULT_PAGE = 1


class Document(BaseDocument):
    __collection__ = None

    @classmethod
    async def find_one_and_update(cls: Type[D], query: dict, update: dict) -> Optional[D]:
        doc = await cls.db_collection.find_one_and_update(query, update)
        if doc:
            return cls(doc)
        return None

    @classmethod
    async def find_one(cls: Type[D], query: dict,
                       sort: Optional[dict] = None, expand: Optional[list] = None) -> Optional[D]:
        if expand:
            return await cls.aggregate_find_one(query, sort=sort, expand=expand)
        else:
            item = await cls._find_one(query=query, sort=sort)
        if item:
            return cls(item)
        return None

    @classmethod
    async def get_by_id(cls: Type[D], oid: ObjectId, expand: Optional[list] = None) -> Optional[D]:
        _id = oid
        item = await cls.find_one({'_id': _id}, expand=expand)
        return item

    @classmethod
    async def find(cls: Type[D], query, sort: dict = None, skip=0, limit=0,
                   expand: Optional[list] = None, as_values: bool = False) -> Union[List[D], List[Dict]]:
        out = []
        query = cls._wrap_query(query)
        if as_values:
            items = await cls._find(query, sort=sort, skip=skip, limit=limit)
            for item in items:
                out.append(item)

        elif expand:
            return await cls.aggregate_find(query, sort=sort, expand=expand, skip=skip, limit=limit)
        else:
            items = await cls._find(query, sort=sort, skip=skip, limit=limit)
            for item in items:
                out.append(cls(item))
        return out

    @classmethod
    async def count(cls: Type[D], query: dict = None, *args, **kwargs) -> int:
        if query is None:
            query = {}
        else:
            query = cls._wrap_query(query)

        return await cls.db_collection.count_documents(query, *args, **kwargs)

    async def delete(self):
        oid = self.get('_id')
        if not oid:
            return
        oid = ObjectId(oid)
        return await self.db_collection.delete_one({'_id': oid})

    @classmethod
    async def delete_many(cls, query: dict, *args, **kwargs):
        assert query, 'empty query'
        query = cls._wrap_query(query)
        return await cls.db_collection.delete_many(query, *args, **kwargs)

    async def pre_save(self, data):
        pass

    async def save(self):
        if not self.has_changes() and self.get('_id'):
            return

        oid = self.get('_id')
        create_new = False

        if not oid:
            create_new = True
        else:
            item = await self.db_collection.find_one({'_id': oid})
            if not item:
                create_new = True

        errors = await self.validate(all_fields=create_new)
        if errors:
            raise ValidationError(errors=errors)

        if create_new:
            data = self._get_data(exclude=['_id'])
            await self.pre_save(data)
            try:
                result = await self.db_collection.insert_one(data)
            except pymongo.errors.DuplicateKeyError:
                raise ValidationError('Duplicate error')
            oid = result.inserted_id
        else:
            data = self._get_changes(exclude=['_id'])
            await self.pre_save(data)
            try:
                await self.db_collection.update_one({'_id': oid}, {'$set': data})
            except pymongo.errors.DuplicateKeyError:
                raise ValidationError('Duplicate error')

        document = await self.db_collection.find_one({'_id': oid})
        self._set_data(document)

    @classmethod
    def _parse_search_query(cls, params) -> dict:
        query = {}

        if params.get('name'):
            query['name'] = {'$regex': params.get('name'), '$options': 'i'}

        return query

    @classmethod
    def _parse_search_query_sort(cls, params) -> dict:
        return {'name': pymongo.ASCENDING}

    @classmethod
    async def aggregate_find_one(cls, query: dict, expand: list, sort: Optional[dict]):
        result = await cls.aggregate_find(query, expand=expand, sort=sort, skip=0, limit=1)
        if len(result) > 0:
            return result[0]

    @classmethod
    async def aggregate_find(cls, query: dict, sort: Optional[dict] = None,
                             expand: list = None, skip: int = 0, limit: int = 0):
        pipeline = [
            {'$match': query},
            {'$skip': skip},
        ]

        if limit > 0:
            pipeline.append({
                '$limit': limit
            })

        if sort:
            pipeline.append({
                '$sort': sort
            })

        extra_fields = {}

        for exp in expand:
            if isinstance(exp, str):
                field = cls.FIELDS.get(exp)

                target_field = exp
                if target_field.endswith('_id'):
                    target_field = target_field[0: -3]

                if isinstance(field, fields.ObjectIdField) and field.ref:
                    ref = field.ref
                    unwind = True
                    extra_fields[target_field] = fields.DocumentField(schema=ref)
                elif isinstance(field, fields.Collection) and isinstance(field.doc_type, fields.ObjectIdField)\
                        and field.doc_type.ref:
                    ref = field.doc_type.ref
                    unwind = False
                    extra_fields[target_field] = fields.Collection(doc_type=ref)
                else:
                    continue

                pipeline.append({
                    '$lookup': {
                        'from': ref.__collection__,
                        'localField': exp,
                        'foreignField': '_id',
                        'as': target_field
                    }
                })
                if unwind:
                    pipeline.append({
                        '$unwind': {
                            'path': f'${target_field}',
                            'preserveNullAndEmptyArrays': True
                        }
                    })

        out = []
        async for item in cls.db_collection.aggregate(pipeline):
            out.append(cls(item, extra_fields=extra_fields))

        return out

    @classmethod
    async def search(cls, params: dict, expand: Optional[List] = None):
        limit = int(params.get('limit', DEFAULT_LIMIT))
        page = int(params.get('page', DEFAULT_PAGE))
        skip = limit * (page - 1)

        query = cls._parse_search_query(params)
        query_sort = cls._parse_search_query_sort(params)

        total = await cls.count(query)
        if skip >= total:
            skip = 0
            page = 1

        items = []
        if expand:
            for doc in await cls.aggregate_find(query, sort=query_sort, expand=expand, limit=limit, skip=skip):
                items.append(doc)
        else:
            raw_items = await cls._find(query, sort=query_sort, skip=skip, limit=limit)
            for item in raw_items:
                items.append(cls(item))

        return SearchResult(items, limit=limit, page=page, total=total)


class NestedDocument(BaseDocument):
    def __init__(self, parent_id: ObjectId, document=None, extra_fields: dict = None):
        self.__parent_id = parent_id
        super().__init__(document, extra_fields)
        assert self.__collection__, 'Need to set collection name'

    @property
    def parent_id(self):
        return self.__parent_id

    @classproperty
    def collection_field(self):
        return self.__collection__.split('.')[-1]

    async def delete(self):
        oid = self.get('_id')
        return await self.db_collection.update_one({'_id': self.__parent_id},
                                                   {'$pull': {self.collection_field: {'_id': oid}}})

    @classmethod
    async def find(cls: Type[ND], find_query: dict, parent_id: ObjectId = None) -> List[ND]:
        query = {}
        if parent_id:
            query['_id'] = parent_id
        find_query = cls._wrap_query(find_query)

        for k, v in find_query.items():
            query[f'{cls.collection_field}.{k}'] = v

        aggregate_query = [
            {'$unwind': f'${cls.collection_field}'},
            {'$match': query},
            {'$project': {
                '_id': 1,
                cls.collection_field: 1
            }}
        ]

        out = []
        async for item in cls.db_collection.aggregate(aggregate_query):
            document = item[cls.collection_field]
            out.append(cls(parent_id=item.get('_id'), document=document))
        return out

    @classmethod
    async def find_one(cls: Type[ND], find_query: dict, parent_id: ObjectId = None) -> Optional[ND]:
        query = {}
        if parent_id:
            query['_id'] = parent_id
        find_query = cls._wrap_query(find_query)
        for k, v in find_query.items():
            query[f'{cls.collection_field}.{k}'] = v

        aggregate_query = [
            {'$unwind': f'${cls.collection_field}'},
            {'$match': query},
            {'$project': {
                '_id': 1,
                cls.collection_field: 1
            }}
        ]

        async for item in cls.db_collection.aggregate(aggregate_query):
            document = item[cls.collection_field]
            return cls(parent_id=item.get('_id'), document=document)
        return None

    @classmethod
    async def get_by_id(cls: Type[ND], oid: ObjectId, **kwargs) -> Optional[ND]:
        _id = oid
        item = await cls.find_one({'_id': _id})
        return item

    async def save(self):
        oid = self.get('_id')
        create_new = False

        if not oid:
            create_new = True
        else:
            item = await self.get_by_id(oid)
            if not item:
                create_new = True

        errors = await self.validate(all_fields=create_new)
        if errors:
            raise ValidationError(errors=errors)

        if create_new:
            data = self._get_data()
            for k, f in self.FIELDS.items():
                if k in data:
                    continue

                value = f.default() if callable(f.default) else f.default
                if value and k not in data:
                    data[k] = f.loads(value)

            await self.db_collection.update_one({'_id': self.__parent_id},
                                                {'$push': {self.collection_field: data}})
            oid = data.get('_id')
        else:
            data = self._get_data()
            prefix_key = f'{self.collection_field}.$.'
            doc = {prefix_key + k: v for k, v in data.items()}
            await self.db_collection.update_one({'_id': self.__parent_id, f'{self.collection_field}._id': oid},
                                                {'$set': doc})

        item = await self.get_by_id(oid)
        self._set_data(item)
