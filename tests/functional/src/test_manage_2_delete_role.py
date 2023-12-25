from http import HTTPStatus

import pytest


pytestmark = pytest.mark.asyncio


async def test_delete_role(request_to_api, delete_test_data):
    try:
        login_req_body = {"login": "admin", "password": "admin"}
        create_role_req_body = {
            "name": "test_role",
            "can_read_limited": False,
            "can_read_all": True,
            "can_subscribe": False,
            "can_manage": True,
        }
        delete_role_req_body = {"name": "test_role"}

        # подготовка к проверкам
        _, login_resp_body = await request_to_api(
            append_url="/users/login", req_body=login_req_body
        )
        atoken = login_resp_body["access_token"]
        rtoken = login_resp_body["refresh_token"]
        await request_to_api(
            append_url="/manage/roles", req_body=create_role_req_body, atoken=atoken
        )

        # проверка на нормальное удаление роли
        delete_role_status, delete_role_resp_body = await request_to_api(
            append_url="/manage/roles",
            req_body=delete_role_req_body,
            atoken=atoken,
            method="DELETE",
        )
        assert delete_role_status == HTTPStatus.OK
        assert delete_role_resp_body is None

        # проверка на повторное удаление той же роли
        delete_role_status, delete_role_resp_body = await request_to_api(
            append_url="/manage/roles",
            req_body=delete_role_req_body,
            atoken=atoken,
            method="DELETE",
        )
        assert delete_role_status == HTTPStatus.BAD_REQUEST
        assert len(delete_role_resp_body) == 1

        # проверка на удаление роли при искаженном атокене
        delete_role_status, delete_role_resp_body = await request_to_api(
            append_url="/manage/roles",
            req_body=delete_role_req_body,
            atoken="______",
            method="DELETE",
        )
        assert delete_role_status == HTTPStatus.UNPROCESSABLE_ENTITY
        assert len(delete_role_resp_body) == 1

        # проверка на удаление роли при отсутствии атокена
        delete_role_status, delete_role_resp_body = await request_to_api(
            append_url="/manage/roles", req_body=delete_role_req_body, method="DELETE"
        )
        assert delete_role_status == HTTPStatus.UNAUTHORIZED
        assert len(delete_role_resp_body) == 1

        # проверка на подмену атокена ртокеном
        delete_role_status, delete_role_resp_body = await request_to_api(
            append_url="/manage/roles",
            req_body=delete_role_req_body,
            atoken=rtoken,
            method="DELETE",
        )
        assert delete_role_status == HTTPStatus.UNPROCESSABLE_ENTITY
        assert len(delete_role_resp_body) == 1

    finally:
        await delete_test_data()
