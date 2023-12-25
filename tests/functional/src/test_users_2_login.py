from http import HTTPStatus

import pytest


pytestmark = pytest.mark.asyncio


@pytest.mark.parametrize(
    "login_req_body, login_exp_answer",
    [
        (
            {"login": "test", "password": "test"},
            {"status": HTTPStatus.OK, "length": 2},
        ),
        (
            {"login": "______", "password": "test"},
            {"status": HTTPStatus.UNAUTHORIZED, "length": 1},
        ),
        (
            {"login": "test", "password": "______"},
            {"status": HTTPStatus.UNAUTHORIZED, "length": 1},
        ),
        (
            {"______": "test", "password": "test"},
            {"status": HTTPStatus.UNPROCESSABLE_ENTITY, "length": 1},
        ),
        (
            {"login": "test", "______": "test"},
            {"status": HTTPStatus.UNPROCESSABLE_ENTITY, "length": 1},
        ),
    ],
)
async def test_login_validate_fields(
    login_req_body,
    login_exp_answer,
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

        # подготовка к проверкам - регистрация пользователя
        await request_to_api(append_url="/users/signup", req_body=signup_req_body)

        # проверка
        login_status, login_resp_body = await request_to_api(
            append_url="/users/login", req_body=login_req_body
        )
        assert login_status == login_exp_answer["status"]
        assert len(login_resp_body) == login_exp_answer["length"]

    finally:
        await delete_test_data()
