from async_fastapi_jwt_auth import AuthJWT
from fastapi import HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete, update

from utils.save_visit import save_visit
from models.role import Role
from models.user import User
from models.visit import Visit


async def create_role_service(
    data: dict,
    request: Request,
    db: AsyncSession,
    auth: AuthJWT,
) -> None:
    """Создание роли."""
    # проверяем, что такой роли еще не существует
    queryset = await db.execute(select(Role).filter(Role.name == data["name"]))
    queryset = queryset.first()
    if queryset:
        raise HTTPException(status_code=400, detail="This role name already exists")

    # создаем роль
    new_role = Role(**data)
    db.add(new_role)
    await db.commit()
    await db.refresh(new_role)

    # записываем посещение и выходим
    await save_visit(request=request, auth=auth, db=db, action="create_role")


async def delete_role_service(
    data: dict,
    request: Request,
    db: AsyncSession,
    auth: AuthJWT,
) -> None:
    """Удаление роли."""
    # проверяем, что такая роль существует; потом удаляем ее
    queryset = await db.execute(select(Role).filter(Role.name == data["name"]))
    queryset = queryset.first()
    if not queryset:
        raise HTTPException(status_code=400, detail="No such role name")
    await db.execute(delete(Role).filter(Role.name == data["name"]))
    await db.commit()

    # записываем посещение и выходим
    await save_visit(request=request, auth=auth, db=db, action="delete_role")


async def change_role_service(
    data: dict,
    request: Request,
    db: AsyncSession,
    auth: AuthJWT,
) -> None:
    """Изменение роли."""
    # проверяем, что такая роль существует; потом обновляем ее
    queryset = await db.execute(select(Role).filter(Role.name == data["name"]))
    queryset = queryset.first()
    if not queryset:
        raise HTTPException(status_code=400, detail="No such role name")
    await db.execute(update(Role).filter(Role.name == data["name"]).values(**data))
    await db.commit()

    # записываем посещение и выходим
    await save_visit(request=request, auth=auth, db=db, action="change_role")


async def show_roles_service(
    request: Request,
    db: AsyncSession,
    auth: AuthJWT,
) -> list[Role]:
    """Просмотр всех ролей."""
    # получаем роли
    queryset = await db.execute(select(Role))
    roles = queryset.all()
    roles = [role[0] for role in roles]

    # сохраняем посещение и выходим
    await save_visit(request=request, auth=auth, db=db, action="show roles")
    return roles


async def assign_user_role_service(
    data: dict,
    request: Request,
    db: AsyncSession,
    auth: AuthJWT,
) -> None:
    """Назначение роли пользователю."""
    # проверяем наличие пользователя с указанным логином
    queryset = await db.execute(
        select(User).filter(User.login == data["for_user_login"])
    )
    queryset = queryset.first()
    if not queryset:
        raise HTTPException(status_code=400, detail="No such user login")
    user = queryset[0]

    # проверяем, что такая роль существует
    queryset = await db.execute(select(Role).filter(Role.name == data["role_name"]))
    queryset = queryset.first()
    if not queryset:
        raise HTTPException(status_code=400, detail="No such role name")
    role = queryset[0]

    # задаем роль
    user.role_id = role.id
    await db.commit()
    await db.refresh(user)

    # сохраняем посещение и выходим
    await save_visit(request=request, auth=auth, db=db, action="assign user role")


async def deprive_user_role_service(
    data: dict,
    request: Request,
    db: AsyncSession,
    auth: AuthJWT,
) -> None:
    """Лишение пользователя роли."""
    # проверяем наличие пользователя с указанным логином
    queryset = await db.execute(
        select(User).filter(User.login == data["for_user_login"])
    )
    queryset = queryset.first()
    if not queryset:
        raise HTTPException(status_code=400, detail="No such user login")
    user = queryset[0]

    # проверяем, что такая роль существует
    queryset = await db.execute(select(Role).filter(Role.name == data["role_name"]))
    queryset = queryset.first()
    if not queryset:
        raise HTTPException(status_code=400, detail="No such role name")
    role = queryset[0]

    # проверяем, что такая роль закреплена за пользователем и отзываем ее
    if user.role_id != role.id:
        raise HTTPException(status_code=400, detail="This user has no this role")
    user.role_id = None
    await db.commit()
    await db.refresh(user)

    # сохраняем посещение и выходим
    await save_visit(request=request, auth=auth, db=db, action="deprive user role")


async def show_user_rights_service(
    data: dict,
    request: Request,
    db: AsyncSession,
    auth: AuthJWT,
) -> (str, Role):
    """Проверка наличия прав у пользователя."""
    # проверяем наличие пользователя с указанным логином
    queryset = await db.execute(
        select(User).filter(User.login == data["for_user_login"])
    )
    queryset = queryset.first()
    if not queryset:
        raise HTTPException(status_code=400, detail="No such user login")

    # определяем права пользователя
    user = queryset[0]
    if user.role_id:
        queryset = await db.execute(select(Role).filter(Role.id == user.role_id))
        queryset = queryset.first()
        role = queryset[0]
    else:
        role = None

    # сохраняем посещение и выходим
    await save_visit(request=request, auth=auth, db=db, action="check user right")
    return user.login, role


async def delete_test_data_service(
    db: AsyncSession,
) -> None:
    """Удаление тестовых данных."""
    await db.execute(
        delete(User).filter(User.is_superuser == False)
    )  # суперпользователя не удаляем, он нужен для тестов
    await db.execute(delete(Role).filter(True))
    await db.execute(delete(Visit).filter(True))
    await db.commit()
