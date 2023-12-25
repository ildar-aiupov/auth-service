from fastapi import HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from async_fastapi_jwt_auth import AuthJWT
from redis.asyncio import Redis

from core.config import settings
from models.user import User
from models.visit import Visit
from utils.save_visit import save_visit


async def signup_service(data: dict, request: Request, db: AsyncSession) -> User:
    """Регистрация нового пользователя."""
    # проверяем, что такого пользователя еще не существует
    queryset = await db.execute(select(User).filter(User.login == data["login"]))
    queryset = queryset.first()
    if queryset:
        raise HTTPException(
            status_code=400, detail="User with this login already exists"
        )

    # создаем и вносим в БД нового пользователя
    user = User(**data)
    db.add(user)
    await db.commit()
    await db.refresh(user)

    # записываем посещение и выходим
    await save_visit(request=request, user=user, db=db, action="signup")
    return user


async def login_service(
    data: dict,
    request: Request,
    db: AsyncSession,
    auth: AuthJWT,
) -> dict:
    """Вход в аккаунт (обмен логина и пароля на пару токенов)."""
    # проверяем наличие пользователя с таким логином
    queryset = await db.execute(select(User).filter(User.login == data["login"]))
    queryset = queryset.first()
    if not queryset:
        raise HTTPException(status_code=401, detail="Users credentials invalid")

    # проверяем правильность пароля
    user = queryset[0]
    if not user.check_password(data["password"]):
        raise HTTPException(status_code=401, detail="Users credentials invalid")

    # создаем пару токенов
    access_token = await auth.create_access_token(subject=user.login)
    refresh_token = await auth.create_refresh_token(subject=user.login)

    # заносим ртокен в БД
    user.valid_rtoken = refresh_token
    await db.commit()
    await db.refresh(user)

    # записываем посещение и выходим
    await save_visit(request=request, user=user, db=db, action="login")
    return {"access_token": access_token, "refresh_token": refresh_token}


async def refresh_service(
    request: Request,
    db: AsyncSession,
    auth: AuthJWT,
) -> dict:
    """Обновление access-токена и refresh-токена."""
    # получаем пользователя из ртокена
    current_user_login = await auth.get_jwt_subject()
    queryset = await db.execute(select(User).filter(User.login == current_user_login))
    user = queryset.first()[0]

    # проверяем соответствие ртокена
    user_rtoken_jti = await auth.get_jti(user.valid_rtoken)
    received_rtoken_jti = (await auth.get_raw_jwt())["jti"]
    if user_rtoken_jti != received_rtoken_jti:
        raise HTTPException(status_code=401, detail="Users credentials invalid")

    # создаем новую пару токенов
    new_access_token = await auth.create_access_token(subject=current_user_login)
    new_refresh_token = await auth.create_refresh_token(subject=current_user_login)

    # обновляем ртокен в БД
    user.valid_rtoken = new_refresh_token
    await db.commit()
    await db.refresh(user)

    # записываем посещение и выходим
    await save_visit(request=request, user=user, db=db, action="refresh")
    return {"access_token": new_access_token, "refresh_token": new_refresh_token}


async def logout_service(
    request: Request,
    redis: Redis,
    db: AsyncSession,
    auth: AuthJWT,
) -> None:
    """Выход пользователя из аккаунта."""
    # записываем посещение
    await save_visit(request=request, auth=auth, db=db, action="logout")

    # вносим атокен в черный список
    received_atoken_jti = (await auth.get_raw_jwt())["jti"]
    await redis.set(
        name=str(received_atoken_jti),
        value="invalid_atoken_jti",
        ex=settings.redis_cache_time,
    )


async def change_user_info_service(
    data: dict,
    request: Request,
    db: AsyncSession,
    auth: AuthJWT,
) -> None:
    """Изменение логина или пароля."""
    # проверяем наличие пользователя с таким логином
    queryset = await db.execute(select(User).filter(User.login == data["login"]))
    queryset = queryset.first()
    if not queryset:
        raise HTTPException(status_code=401, detail="Users credentials invalid")

    # проверяем правильность его пароля
    user = queryset[0]
    if not user.check_password(data["password"]):
        raise HTTPException(status_code=401, detail="Users credentials invalid")

    # получаем пользователя из полученного логина
    queryset = await db.execute(select(User).filter(User.login == data["login"]))
    user = queryset.first()[0]

    # Обновляем данные пользователя и удаляем старый ртокен, так как он привязан к устаревшей информации о пользователе
    if data["new_first_name"]:
        user.first_name = data["new_first_name"]
    if data["new_last_name"]:
        user.last_name = data["new_last_name"]
    if data["new_password"]:
        user.set_password_hash(data["new_password"])
    if data["new_login"]:
        user.login = data["new_login"]
    user.valid_rtoken = None
    await db.commit()
    await db.refresh(user)

    # записываем посещение
    await save_visit(request=request, user=user, db=db, action="change_user_info")


async def history_service(
    request: Request,
    db: AsyncSession,
    auth: AuthJWT,
) -> list[Visit]:
    """Получение пользователем истории своих входов в аккаунт."""
    # получаем пользователя из атокена
    current_user_login = await auth.get_jwt_subject()
    queryset = await db.execute(select(User).filter(User.login == current_user_login))
    user = queryset.first()[0]

    # получаем историю для этого пользователя
    queryset = await db.execute(select(Visit).filter(Visit.user_id == str(user.id)))
    visits = queryset.all()
    visits = [visit[0] for visit in visits]

    # сохраняем посещение и выходим
    await save_visit(request=request, user=user, db=db, action="history")
    return visits
