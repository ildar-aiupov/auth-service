from http import HTTPStatus

import pytest


pytestmark = pytest.mark.asyncio


async def test_show_roles(request_to_api, delete_test_data):
    try:
        login_req_body = {"login": "admin", "password": "admin"}
        create_role_req_body = {
            "name": "test_role",
            "can_read_limited": False,
            "can_read_all": True,
            "can_subscribe": False,
            "can_manage": True,
        }
        create_role_req_body_2 = {
            "name": "test_role_2",
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
        await request_to_api(
            append_url="/manage/roles", req_body=create_role_req_body, atoken=atoken
        )
        await request_to_api(
            append_url="/manage/roles", req_body=create_role_req_body_2, atoken=atoken
        )

        # проверка на нормальный показ ролей
        show_role_status, show_role_resp_body = await request_to_api(
            append_url="/manage/roles", req_body=None, atoken=atoken, method="GET"
        )
        assert show_role_status == HTTPStatus.OK
        assert len(show_role_resp_body) == 2

        # проверка на показ ролей при искаженном атокене
        show_role_status, show_role_resp_body = await request_to_api(
            append_url="/manage/roles", req_body=None, atoken="______", method="GET"
        )
        assert show_role_status == HTTPStatus.UNPROCESSABLE_ENTITY
        assert len(show_role_resp_body) == 1

        # проверка на показ ролей при отсутствии атокена
        show_role_status, show_role_resp_body = await request_to_api(
            append_url="/manage/roles", req_body=None, method="GET"
        )
        assert show_role_status == HTTPStatus.UNAUTHORIZED
        assert len(show_role_resp_body) == 1

        # проверка на подмену атокена ртокеном
        show_role_status, show_role_resp_body = await request_to_api(
            append_url="/manage/roles", req_body=None, atoken=rtoken, method="GET"
        )
        assert show_role_status == HTTPStatus.UNPROCESSABLE_ENTITY
        assert len(show_role_resp_body) == 1

    finally:
        await delete_test_data()
