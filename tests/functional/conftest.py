import asyncio

import pytest

from .fixtures.api_fixtures import request_to_api, delete_test_data


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()
