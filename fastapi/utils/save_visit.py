from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from async_fastapi_jwt_auth import AuthJWT

from db.postgres import get_session
from models.user import User
from models.visit import Visit


async def save_visit(
    request: Request,
    action: str,
    user: User | None = None,
    auth: AuthJWT | None = None,
    db: AsyncSession = Depends(get_session),
):
    if not user and not auth:
        return

    # если есть auth, то получаем пользователя из него (из ртокена).
    # наличие user не проверяем - он либо пришел с вызовом функции (вместо auth),
    # либо будет получен из auth дальше
    if auth:
        current_user_login = await auth.get_jwt_subject()
        queryset = await db.execute(
            select(User).filter(User.login == current_user_login)
        )
        user = queryset.first()[0]

    # записываем данные о посещении
    visit = Visit(
        user_id=str(user.id),
        action=action,
        user_agent=request.headers.get("user-agent"),
    )
    db.add(visit)
    await db.commit()
    await db.refresh(visit)
