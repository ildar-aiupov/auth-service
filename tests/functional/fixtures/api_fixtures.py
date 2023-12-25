import aiohttp
import pytest

from ..settings import settings


@pytest.fixture
async def request_to_api():
    async def inner(
        append_url: str,
        req_body: dict = None,
        atoken: str = None,
        rtoken: str = None,
        method: str = "POST",
        params: dict = None,
    ):
        async with aiohttp.ClientSession() as session:
            url = settings.base_url + append_url
            headers = {}
            if atoken or rtoken:
                headers["Authorization"] = "Bearer " + (atoken or rtoken)
            async with session.request(
                method=method, url=url, json=req_body, headers=headers, params=params
            ) as response:
                status = response.status
                resp_body = await response.json()
        return status, resp_body

    return inner


@pytest.fixture
async def delete_test_data():
    async def inner():
        async with aiohttp.ClientSession() as session:
            url = settings.base_url + "/manage/delete_test_data"
            async with session.delete(url) as response:
                status = response.status
        return status

    return inner
