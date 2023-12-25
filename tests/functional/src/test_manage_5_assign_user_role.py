from http import HTTPStatus

import pytest


pytestmark = pytest.mark.asyncio


@pytest.mark.parametrize(
    "assign_req_body, assign_exp_answer",
    [
        (
            {"for_user_login": "test", "role_name": "test_role"},
            {"status": HTTPStatus.OK, "length": None},
        ),
        (
            {"for_user_login": "______", "role_name": "test_role"},
            {"status": HTTPStatus.BAD_REQUEST, "length": 1},
        ),
        (
            {"for_user_login": "test", "role_name": "______"},
            {"status": HTTPStatus.BAD_REQUEST, "length": 1},
        ),
        (
            {"______": "test", "role_name": "test_role"},
            {"status": HTTPStatus.UNPROCESSABLE_ENTITY, "length": 1},
        ),
        (
            {"for_user_login": "test", "______": "test_role"},
            {"status": HTTPStatus.UNPROCESSABLE_ENTITY, "length": 1},
        ),
    ],
)
async def test_assign_user_role_validate_values(
    assign_req_body, assign_exp_answer, request_to_api, delete_test_data
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

        # проверка
        assign_status, assign_resp_body = await request_to_api(
            append_url="/manage/assign_user_role",
            req_body=assign_req_body,
            atoken=atoken,
        )
        assert assign_status == assign_exp_answer["status"]
        if assign_resp_body:
            assert len(assign_resp_body) == assign_exp_answer["length"]

    finally:
        await delete_test_data()


async def test_assign_user_role_check_tokens(request_to_api, delete_test_data):
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

        # проверка на запрос при искаженном атокене
        assign_status, assign_resp_body = await request_to_api(
            append_url="/manage/assign_user_role",
            req_body=assign_req_body,
            atoken="______",
        )
        assert assign_status == HTTPStatus.UNPROCESSABLE_ENTITY
        assert len(assign_resp_body) == 1

        # проверка на запрос при отсутствии атокена
        assign_status, assign_resp_body = await request_to_api(
            append_url="/manage/assign_user_role",
            req_body=assign_req_body,
        )
        assert assign_status == HTTPStatus.UNAUTHORIZED
        assert len(assign_resp_body) == 1

        # проверка на подмену атокена ртокеном
        assign_status, assign_resp_body = await request_to_api(
            append_url="/manage/assign_user_role",
            req_body=assign_req_body,
            atoken=rtoken,
        )
        assert assign_status == HTTPStatus.UNPROCESSABLE_ENTITY
        assert len(assign_resp_body) == 1

    finally:
        await delete_test_data()
