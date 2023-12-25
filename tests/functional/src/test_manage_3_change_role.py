from http import HTTPStatus

import pytest


pytestmark = pytest.mark.asyncio


async def test_change_role(request_to_api, delete_test_data):
    try:
        login_req_body = {"login": "admin", "password": "admin"}
        create_role_req_body = {
            "name": "test_role",
            "can_read_limited": False,
            "can_read_all": True,
            "can_subscribe": False,
            "can_manage": True,
        }
        change_role_req_body = {
            "name": "test_role",
            "can_read_limited": False,
            "can_read_all": False,
            "can_subscribe": False,
            "can_manage": False,
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

        # проверка на нормальное изменение роли
        change_role_status, change_role_resp_body = await request_to_api(
            append_url="/manage/roles",
            req_body=change_role_req_body,
            atoken=atoken,
            method="PUT",
        )
        assert change_role_status == HTTPStatus.OK
        assert change_role_resp_body is None

        # проверка на изменение роли при искаженном атокене
        change_role_status, change_role_resp_body = await request_to_api(
            append_url="/manage/roles",
            req_body=change_role_req_body,
            atoken="______",
            method="PUT",
        )
        assert change_role_status == HTTPStatus.UNPROCESSABLE_ENTITY
        assert len(change_role_resp_body) == 1

        # проверка на изменение роли при отсутствии атокена
        change_role_status, change_role_resp_body = await request_to_api(
            append_url="/manage/roles", req_body=change_role_req_body, method="PUT"
        )
        assert change_role_status == HTTPStatus.UNAUTHORIZED
        assert len(change_role_resp_body) == 1

        # проверка на подмену атокена ртокеном
        change_role_status, change_role_resp_body = await request_to_api(
            append_url="/manage/roles",
            req_body=change_role_req_body,
            atoken=rtoken,
            method="PUT",
        )
        assert change_role_status == HTTPStatus.UNPROCESSABLE_ENTITY
        assert len(change_role_resp_body) == 1

        # проверка на изменение отсутствующей роли
        change_role_req_body["name"] = "______"
        change_role_status, change_role_resp_body = await request_to_api(
            append_url="/manage/roles",
            req_body=change_role_req_body,
            atoken=atoken,
            method="PUT",
        )
        assert change_role_status == HTTPStatus.BAD_REQUEST
        assert len(change_role_resp_body) == 1

    finally:
        await delete_test_data()
