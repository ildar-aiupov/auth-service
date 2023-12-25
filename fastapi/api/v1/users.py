from fastapi import APIRouter, Depends, status, Request, Query
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession
from async_fastapi_jwt_auth import AuthJWT
from redis.asyncio import Redis

from db.redis_db import get_redis
from db.postgres import get_session
from schemas.requests import (
    SignupReq,
    LoginReq,
    ChangeUserInfoReq,
)
from schemas.responses import SignupResp, TokenResp, HistoryResp
from services.users import (
    signup_service,
    login_service,
    refresh_service,
    logout_service,
    change_user_info_service,
    history_service,
)


router = APIRouter()


@router.post("/signup", response_model=SignupResp, status_code=status.HTTP_201_CREATED)
async def signup(
    signup_req: SignupReq, request: Request, db: AsyncSession = Depends(get_session)
) -> SignupResp:
    """Регистрация нового пользователя."""
    data = jsonable_encoder(signup_req)
    return await signup_service(data=data, request=request, db=db)


@router.post("/login", response_model=TokenResp, status_code=status.HTTP_200_OK)
async def login(
    login_req: LoginReq,
    request: Request,
    db: AsyncSession = Depends(get_session),
    auth: AuthJWT = Depends(),
) -> TokenResp:
    """Вход в аккаунт (обмен логина и пароля на пару токенов)."""
    data = jsonable_encoder(login_req)
    return await login_service(data=data, request=request, db=db, auth=auth)


@router.post("/refresh", response_model=TokenResp, status_code=status.HTTP_200_OK)
async def refresh(
    request: Request,
    db: AsyncSession = Depends(get_session),
    auth: AuthJWT = Depends(),
) -> TokenResp:
    """Обновление access-токена и refresh-токена."""
    await auth.jwt_refresh_token_required()
    return await refresh_service(request=request, db=db, auth=auth)


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(
    request: Request,
    redis: Redis = Depends(get_redis),
    db: AsyncSession = Depends(get_session),
    auth: AuthJWT = Depends(),
) -> None:
    """Выход пользователя из аккаунта."""
    await auth.jwt_required()
    await logout_service(request=request, redis=redis, db=db, auth=auth)


@router.post("/change_user_info", status_code=status.HTTP_200_OK)
async def change_user_info(
    change_user_info_req: ChangeUserInfoReq,
    request: Request,
    db: AsyncSession = Depends(get_session),
    auth: AuthJWT = Depends(),
) -> None:
    """Изменение логина или пароля."""
    data = jsonable_encoder(change_user_info_req)
    await change_user_info_service(data=data, request=request, db=db, auth=auth)


@router.get(
    "/history", response_model=list[HistoryResp], status_code=status.HTTP_200_OK
)
async def history(
    request: Request,
    db: AsyncSession = Depends(get_session),
    auth: AuthJWT = Depends(),
    page: int = Query(ge=0, default=0),
    size: int = Query(ge=1, default=10),
) -> HistoryResp:
    """Получение пользователем истории своих входов в аккаунт."""
    await auth.jwt_required()
    # получаем и преобразуем в представление список посещений
    visits = await history_service(request=request, db=db, auth=auth)
    offset_min = page * size
    offset_max = (page + 1) * size
    return [
        HistoryResp(
            action=visit.action,
            user_agent=visit.user_agent,
            created_at=str(visit.created_at),
        )
        for visit in visits[offset_min:offset_max]
    ]
