from http import HTTPStatus

import pytest


pytestmark = pytest.mark.asyncio


async def test_logout_check_tokens(
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
        atoken = login_resp_body["access_token"]

        # проверка на нормальный логаут
        logout_status, logout_resp_body = await request_to_api(
            append_url="/users/logout", atoken=atoken
        )
        assert logout_status == HTTPStatus.OK
        assert logout_resp_body is None

        # проверка на повторный логаут с тем же атокеном
        logout_status, logout_resp_body = await request_to_api(
            append_url="/users/logout", atoken=atoken
        )
        assert logout_status == HTTPStatus.UNAUTHORIZED
        assert len(logout_resp_body) == 1

        # проверка на logout при искаженном атокене
        logout_status, logout_resp_body = await request_to_api(
            append_url="/users/logout", atoken="______"
        )
        assert logout_status == HTTPStatus.UNPROCESSABLE_ENTITY
        assert len(logout_resp_body) == 1

        # проверка на logout при отсутствии атокена
        logout_status, logout_resp_body = await request_to_api(
            append_url="/users/logout"
        )
        assert logout_status == HTTPStatus.UNAUTHORIZED
        assert len(logout_resp_body) == 1

        # проверка на подмену атокена ртокеном
        _, login_resp_body = await request_to_api(
            append_url="/users/login", req_body=login_req_body
        )
        rtoken = login_resp_body["refresh_token"]
        logout_status, logout_resp_body = await request_to_api(
            append_url="/users/logout", atoken=rtoken
        )
        assert logout_status == HTTPStatus.UNPROCESSABLE_ENTITY
        assert len(logout_resp_body) == 1

    finally:
        await delete_test_data()
