from http import HTTPStatus

import pytest


pytestmark = pytest.mark.asyncio


@pytest.mark.parametrize(
    "change_req_body, change_exp_answer",
    [
        (
            {"login": "test", "password": "test", "new_login": "test"},
            {"status": HTTPStatus.OK, "length": 0},
        ),
        (
            {"login": "______", "password": "test", "new_login": "test"},
            {"status": HTTPStatus.UNAUTHORIZED, "length": 1},
        ),
        (
            {"login": "test", "password": "______", "new_login": "test"},
            {"status": HTTPStatus.UNAUTHORIZED, "length": 1},
        ),
        (
            {"______": "test", "password": "test", "new_login": "test"},
            {"status": HTTPStatus.UNPROCESSABLE_ENTITY, "length": 1},
        ),
        (
            {"login": "test", "______": "test", "new_login": "test"},
            {"status": HTTPStatus.UNPROCESSABLE_ENTITY, "length": 1},
        ),
    ],
)
async def test_change_user_info_validate_fields(
    change_req_body,
    change_exp_answer,
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
        change_status, change_resp_body = await request_to_api(
            append_url="/users/change_user_info", req_body=change_req_body
        )
        assert change_status == change_exp_answer["status"]
        if change_resp_body:  # боди есть только при ошибках; при успехе оно - None
            assert len(change_resp_body) == change_exp_answer["length"]

    finally:
        await delete_test_data()
