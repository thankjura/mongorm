import asyncio
import os

import pytest
from motor.motor_asyncio import AsyncIOMotorClient

from mongorm.db import Connection

MONGO_DB_HOST = os.environ.get('TEST_MONGO_DB_HOST', 'localhost')
MONGO_DB_PORT = os.environ.get('TEST_MONGO_DB_PORT', 27017)
MONGO_DB_NAME = os.environ.get('TEST_MONGO_DB_NAME', 'test_mongorm')

MONGO_URI = f'mongodb://{MONGO_DB_HOST}:{MONGO_DB_PORT}'
MONGO_CONFIG_PARAMS = dict(host=MONGO_DB_HOST, port=MONGO_DB_PORT, database=MONGO_DB_NAME)


@pytest.fixture
async def mongo_db():
    client = AsyncIOMotorClient(MONGO_URI)
    Connection().set_database(client[MONGO_DB_NAME])
    yield
    await asyncio.gather(*asyncio.all_tasks() - {asyncio.current_task()})
    Connection().unset_database()
    await client.drop_database(MONGO_DB_NAME)
