from http import HTTPStatus

import pytest


pytestmark = pytest.mark.asyncio


@pytest.mark.parametrize(
    "show_req_body, show_exp_answer",
    [
        (
            {"for_user_login": "test"},
            {"status": HTTPStatus.OK, "length": 5},
        ),
        (
            {"for_user_login": "______"},
            {"status": HTTPStatus.BAD_REQUEST, "length": 1},
        ),
        (
            {"______": "test"},
            {"status": HTTPStatus.UNPROCESSABLE_ENTITY, "length": 1},
        ),
    ],
)
async def test_show_user_rights_validate_values(
    show_req_body, show_exp_answer, request_to_api, delete_test_data
):
    try:
        signup_req_body = {
            "login": "test",
            "password": "test",
            "first_name": "test",
            "last_name": "test",
        }
        login_req_body = {"login": "admin", "password": "admin"}
        create_role_req_body = {
            "name": "test_role",
            "can_read_limited": False,
            "can_read_all": True,
            "can_subscribe": False,
            "can_manage": True,
        }
        assign_req_body = {"for_user_login": "test", "role_name": "test_role"}

        # подготовка к проверкам
        await request_to_api(append_url="/users/signup", req_body=signup_req_body)
        _, login_resp_body = await request_to_api(
            append_url="/users/login", req_body=login_req_body
        )
        atoken = login_resp_body["access_token"]
        rtoken = login_resp_body["refresh_token"]
        await request_to_api(
            append_url="/manage/roles", req_body=create_role_req_body, atoken=atoken
        )
        await request_to_api(
            append_url="/manage/assign_user_role",
            req_body=assign_req_body,
            atoken=atoken,
        )

        # проверка
        show_status, show_resp_body = await request_to_api(
            append_url="/manage/show_user_rights", req_body=show_req_body, atoken=atoken
        )
        assert show_status == show_exp_answer["status"]
        if show_resp_body:
            assert len(show_resp_body) == show_exp_answer["length"]

    finally:
        await delete_test_data()


async def test_show_user_role_check_tokens(request_to_api, delete_test_data):
    try:
        signup_req_body = {
            "login": "test",
            "password": "test",
            "first_name": "test",
            "last_name": "test",
        }
        login_req_body = {"login": "admin", "password": "admin"}
        create_role_req_body = {
            "name": "test_role",
            "can_read_limited": False,
            "can_read_all": True,
            "can_subscribe": False,
            "can_manage": True,
        }
        assign_req_body = {"for_user_login": "test", "role_name": "test_role"}
        show_req_body = {"for_user_login": "test"}

        # подготовка к проверкам
        await request_to_api(append_url="/users/signup", req_body=signup_req_body)
        _, login_resp_body = await request_to_api(
            append_url="/users/login", req_body=login_req_body
        )
        atoken = login_resp_body["access_token"]
        rtoken = login_resp_body["refresh_token"]
        await request_to_api(
            append_url="/manage/roles", req_body=create_role_req_body, atoken=atoken
        )
        await request_to_api(
            append_url="/manage/assign_user_role",
            req_body=assign_req_body,
            atoken=atoken,
        )

        # проверка на запрос при искаженном атокене
        show_status, show_resp_body = await request_to_api(
            append_url="/manage/show_user_rights",
            req_body=show_req_body,
            atoken="______",
        )
        assert show_status == HTTPStatus.UNPROCESSABLE_ENTITY
        assert len(show_resp_body) == 1

        # проверка на запрос при отсутствии атокена
        show_status, show_resp_body = await request_to_api(
            append_url="/manage/show_user_rights",
            req_body=show_req_body,
        )
        assert show_status == HTTPStatus.UNAUTHORIZED
        assert len(show_resp_body) == 1

        # проверка на подмену атокена ртокеном
        show_status, show_resp_body = await request_to_api(
            append_url="/manage/show_user_rights",
            req_body=show_req_body,
            atoken=rtoken,
        )
        assert show_status == HTTPStatus.UNPROCESSABLE_ENTITY
        assert len(show_resp_body) == 1

    finally:
        await delete_test_data()
