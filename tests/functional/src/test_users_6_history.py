from http import HTTPStatus

import pytest


pytestmark = pytest.mark.asyncio


@pytest.mark.parametrize(
    "history_params, history_exp_answer",
    [
        (
            {},
            {"status": HTTPStatus.OK, "length": 10},
        ),
        (
            {"page": 1, "size": 9},
            {"status": HTTPStatus.OK, "length": 6},
        ),
        (
            {"page": 1, "size": 1000},
            {"status": HTTPStatus.OK, "length": 0},
        ),
        (
            {"page": 0, "size": 1000},
            {"status": HTTPStatus.OK, "length": 15},
        ),
        (
            {"page": 1000, "size": 1},
            {"status": HTTPStatus.OK, "length": 0},
        ),
        (
            {"page": -1, "size": 1},
            {"status": HTTPStatus.UNPROCESSABLE_ENTITY, "length": 1},
        ),
        (
            {"page": 0, "size": 0},
            {"status": HTTPStatus.UNPROCESSABLE_ENTITY, "length": 1},
        ),
        (
            {"page": "______", "size": 1},
            {"status": HTTPStatus.UNPROCESSABLE_ENTITY, "length": 1},
        ),
        (
            {"page": 0, "size": "______"},
            {"status": HTTPStatus.UNPROCESSABLE_ENTITY, "length": 1},
        ),
    ],
)
async def test_history_validate_values(
    history_params,
    history_exp_answer,
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

        # подготовка к проверкам - создание 15 посещений, получение атокена
        await request_to_api(append_url="/users/signup", req_body=signup_req_body)
        for _ in range(14):
            __, login_resp_body = await request_to_api(
                append_url="/users/login", req_body=login_req_body
            )
        atoken = login_resp_body["access_token"]

        # проверка
        resp_status, resp_body = await request_to_api(
            append_url="/users/history",
            atoken=atoken,
            params=history_params,
            method="GET",
        )
        assert resp_status == history_exp_answer["status"]
        assert len(resp_body) == history_exp_answer["length"]

    finally:
        await delete_test_data()


async def test_history_check_tokens(
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
        __, login_resp_body = await request_to_api(
            append_url="/users/login", req_body=login_req_body
        )
        atoken = login_resp_body["access_token"]
        rtoken = login_resp_body["refresh_token"]

        # проверка на запрос с искаженным атокеном
        history_status, history_resp_body = await request_to_api(
            append_url="/users/history", atoken="______", method="GET"
        )
        assert history_status == HTTPStatus.UNPROCESSABLE_ENTITY
        assert len(history_resp_body) == 1

        # проверка на действие при отсутствии атокена
        history_status, history_resp_body = await request_to_api(
            append_url="/users/history", method="GET"
        )
        assert history_status == HTTPStatus.UNAUTHORIZED
        assert len(history_resp_body) == 1

        # проверка на подмену атокена ртокеном
        history_status, history_resp_body = await request_to_api(
            append_url="/users/history", atoken=rtoken, method="GET"
        )
        assert history_status == HTTPStatus.UNPROCESSABLE_ENTITY
        assert len(history_resp_body) == 1

    finally:
        await delete_test_data()
