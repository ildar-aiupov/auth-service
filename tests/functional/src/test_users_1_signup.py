from http import HTTPStatus

import pytest


pytestmark = pytest.mark.asyncio


@pytest.mark.parametrize(
    "signup_req_body, signup_exp_answer",
    [
        (
            {
                "login": "test",
                "password": "test",
                "first_name": "test",
                "last_name": "test",
            },
            {"status": HTTPStatus.CREATED, "length": 3},
        ),
        (
            {
                "______": "test",
                "password": "test",
                "first_name": "test",
                "last_name": "test",
            },
            {"status": HTTPStatus.UNPROCESSABLE_ENTITY, "length": 1},
        ),
        (
            {
                "login": "test",
                "______": "test",
                "first_name": "test",
                "last_name": "test",
            },
            {"status": HTTPStatus.UNPROCESSABLE_ENTITY, "length": 1},
        ),
        (
            {
                "login": "test",
                "password": "test",
                "______": "test",
                "last_name": "test",
            },
            {"status": HTTPStatus.UNPROCESSABLE_ENTITY, "length": 1},
        ),
        (
            {
                "login": "test",
                "password": "test",
                "first_name": "test",
                "______": "test",
            },
            {"status": HTTPStatus.UNPROCESSABLE_ENTITY, "length": 1},
        ),
    ],
)
async def test_signup_validate_fields(
    signup_req_body, signup_exp_answer, request_to_api, delete_test_data
):
    try:
        signup_status, signup_resp_body = await request_to_api(
            append_url="/users/signup", req_body=signup_req_body
        )
        assert signup_status == signup_exp_answer["status"]
        assert len(signup_resp_body) == signup_exp_answer["length"]

    finally:
        await delete_test_data()


async def test_signup_doubling(request_to_api, delete_test_data):
    try:
        signup_req_body = {
            "login": "test",
            "password": "test",
            "first_name": "test",
            "last_name": "test",
        }

        # подготовка к проверке - регистрация пользователя
        await request_to_api(append_url="/users/signup", req_body=signup_req_body)

        # проверка - повторная регистрация того же пользователя
        signup_status, signup_resp_body = await request_to_api(
            append_url="/users/signup", req_body=signup_req_body
        )
        assert signup_status == HTTPStatus.BAD_REQUEST
        assert len(signup_resp_body) == 1

    finally:
        await delete_test_data()
