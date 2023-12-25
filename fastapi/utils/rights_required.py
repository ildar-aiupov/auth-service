import functools

from fastapi import HTTPException
from sqlalchemy.future import select

from models.user import User
from models.role import Role


def rights_required(rights: list[str]):
    def func_decor(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            auth = kwargs.get("auth")
            user = kwargs.get("user")
            db = kwargs.get("db")
            await auth.jwt_required()
            if not user and not auth:
                return await func(*args, **kwargs)
            # если есть auth, то получаем пользователя из него (из ртокена).
            # наличие user не проверяем - он либо пришел с вызовом функции (вместо auth),
            # либо будет получен из auth дальше
            if auth:
                current_user_login = await auth.get_jwt_subject()
                queryset = await db.execute(
                    select(User).filter(User.login == current_user_login)
                )
                user = queryset.first()[0]

            # сразу же пропускаем суперпользователя
            if user.is_superuser:
                return await func(*args, **kwargs)

            # проверяем - имеет ли пользователь указанное право
            queryset = await db.execute(select(Role).filter(Role.id == user.role_id))
            queryset = queryset.first()
            if not queryset:  # при отсутствии ролей никаких прав нет
                raise HTTPException(
                    status_code=401, detail="User has no right for this action"
                )
            role = queryset[0]
            for right in rights:
                if not getattr(role, right):
                    raise HTTPException(
                        status_code=401, detail="User has no right for this action"
                    )
            return await func(*args, **kwargs)

        return wrapper

    return func_decor
