from http import HTTPStatus

import pytest


pytestmark = pytest.mark.asyncio


async def test_create_role(request_to_api, delete_test_data):
    try:
        login_req_body = {"login": "admin", "password": "admin"}
        create_role_req_body = {
            "name": "test_role",
            "can_read_limited": False,
            "can_read_all": True,
            "can_subscribe": False,
            "can_manage": True,
        }

        # подготовка к проверкам
        _, login_resp_body = await request_to_api(
            append_url="/users/login", req_body=login_req_body
        )
        atoken = login_resp_body["access_token"]
        rtoken = login_resp_body["refresh_token"]

        # проверка на нормальное создание роли
        create_role_status, create_role_resp_body = await request_to_api(
            append_url="/manage/roles", req_body=create_role_req_body, atoken=atoken
        )
        assert create_role_status == HTTPStatus.CREATED
        assert create_role_resp_body is None

        # проверка на повторное создание той же роли
        create_role_status, create_role_resp_body = await request_to_api(
            append_url="/manage/roles", req_body=create_role_req_body, atoken=atoken
        )
        assert create_role_status == HTTPStatus.BAD_REQUEST
        assert len(create_role_resp_body) == 1

        # проверка на создание роли при искаженном атокене
        create_role_status, create_role_resp_body = await request_to_api(
            append_url="/manage/roles", req_body=create_role_req_body, atoken="______"
        )
        assert create_role_status == HTTPStatus.UNPROCESSABLE_ENTITY
        assert len(create_role_resp_body) == 1

        # проверка на создание роли при отсутствии атокена
        create_role_status, create_role_resp_body = await request_to_api(
            append_url="/manage/roles", req_body=create_role_req_body
        )
        assert create_role_status == HTTPStatus.UNAUTHORIZED
        assert len(create_role_resp_body) == 1

        # проверка на подмену атокена ртокеном
        create_role_status, create_role_resp_body = await request_to_api(
            append_url="/manage/roles", req_body=create_role_req_body, atoken=rtoken
        )
        assert create_role_status == HTTPStatus.UNPROCESSABLE_ENTITY
        assert len(create_role_resp_body) == 1

    finally:
        await delete_test_data()
