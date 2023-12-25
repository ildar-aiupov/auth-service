from http import HTTPStatus

import pytest


pytestmark = pytest.mark.asyncio


async def test_refresh_check_tokens(
    request_to_api,
    delete_test_data,
):
    try:
        signup_req_body = {
            "login": "test",
            "password": "test",
            "first_name": "test",
            "last_name": "test",
        }
        login_req_body = {
            "login": "test",
            "password": "test",
        }

        # подготовка к проверкам
        await request_to_api(append_url="/users/signup", req_body=signup_req_body)
        _, login_resp_body = await request_to_api(
            append_url="/users/login", req_body=login_req_body
        )
        rtoken = login_resp_body["refresh_token"]

        # проверка на нормальное обновление ртокена
        refresh_status, refresh_resp_body = await request_to_api(
            append_url="/users/refresh", rtoken=rtoken
        )
        assert refresh_status == HTTPStatus.OK
        assert len(refresh_resp_body) == 2

        # проверка на использование устаревшего ртокена
        refresh_status, refresh_resp_body = await request_to_api(
            append_url="/users/refresh", rtoken=rtoken
        )
        assert refresh_status == HTTPStatus.UNAUTHORIZED
        assert len(refresh_resp_body) == 1

        # проверка на действие при искаженном ртокене
        refresh_status, refresh_resp_body = await request_to_api(
            append_url="/users/refresh", rtoken="______"
        )
        assert refresh_status == HTTPStatus.UNPROCESSABLE_ENTITY
        assert len(refresh_resp_body) == 1

        # проверка на действие при отсутствии ртокена
        refresh_status, refresh_resp_body = await request_to_api(
            append_url="/users/refresh"
        )
        assert refresh_status == HTTPStatus.UNAUTHORIZED
        assert len(refresh_resp_body) == 1

        # проверка на подмену ртокена атокеном
        _, login_resp_body = await request_to_api(
            append_url="/users/login", req_body=login_req_body
        )
        atoken = login_resp_body["access_token"]
        refresh_status, refresh_resp_body = await request_to_api(
            append_url="/users/refresh", rtoken=atoken
        )
        assert refresh_status == HTTPStatus.UNPROCESSABLE_ENTITY
        assert len(refresh_resp_body) == 1

    finally:
        await delete_test_data()
