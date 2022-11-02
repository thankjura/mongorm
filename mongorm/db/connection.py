__all__ = ['Connection']

import asyncio
import logging

from mongorm.utils.singleton import Singleton


logger = logging.getLogger(__name__)


DEFAULT_INDEX_OPTIONS = {
    'background': True
}


class Connection(metaclass=Singleton):
    __indexes: dict = {}

    def __init__(self):
        self.__db = None

    @property
    def db(self):
        if self.__db is not None:
            return self.__db

        raise RuntimeError('Trying to get connection before connection was initialized.')

    def has_connect(self) -> bool:
        return self.__db is not None

    @classmethod
    def create_indexes(cls, collection, indexes):
        cls.__indexes[collection] = indexes
        if cls().has_connect():
            asyncio.create_task(cls().__create_indexes())

    async def __create_indexes(self) -> None:
        while self.__indexes:
            collection, indexes = self.__indexes.popitem()
            for item in indexes:
                logger.debug('try to create index for <%s>: %s', collection, str(item))
                if isinstance(item[-1], dict):
                    options = DEFAULT_INDEX_OPTIONS | item[-1].get('options', {})
                    logger.debug(f'index options for "{item}": {options}')
                    res = await self.__db[collection].create_index(item[:-1], **options)
                else:
                    res = await self.__db[collection].create_index(item, **DEFAULT_INDEX_OPTIONS)

                logger.debug('index creation result: %s', str(res))

    def set_database(self, database):
        assert not self.__db, 'Database already set.'
        self.__db = database

        asyncio.gather(self.__create_indexes())
        # asyncio.create_task(self.__create_indexes())

    def unset_database(self):
        self.__db = None
