from async_fastapi_jwt_auth import AuthJWT
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession

from db.postgres import get_session
from schemas.requests import (
    Create_role_req,
    Delete_role_req,
    Change_role_req,
    Assign_user_role_req,
    Deprive_user_role_req,
    Show_user_rights_req,
)
from schemas.responses import ShowRolesResp, ShowUserRightsResp

from utils.rights_required import rights_required

from core.config import settings
from services.manage import (
    create_role_service,
    delete_role_service,
    change_role_service,
    show_roles_service,
    assign_user_role_service,
    deprive_user_role_service,
    show_user_rights_service,
    delete_test_data_service,
)


router = APIRouter()


@router.post("/roles", status_code=status.HTTP_201_CREATED)
@rights_required(rights=["can_manage"])
async def create_role(
    create_role_req: Create_role_req,
    request: Request,
    db: AsyncSession = Depends(get_session),
    auth: AuthJWT = Depends(),
) -> None:
    """Создание роли."""
    await auth.jwt_required()
    data = jsonable_encoder(create_role_req)
    await create_role_service(data=data, request=request, db=db, auth=auth)


@router.delete("/roles", status_code=status.HTTP_200_OK)
@rights_required(rights=["can_manage"])
async def delete_role(
    delete_role_req: Delete_role_req,
    request: Request,
    db: AsyncSession = Depends(get_session),
    auth: AuthJWT = Depends(),
) -> None:
    """Удаление роли."""
    await auth.jwt_required()
    data = jsonable_encoder(delete_role_req)
    await delete_role_service(data=data, request=request, db=db, auth=auth)


@router.put("/roles", status_code=status.HTTP_200_OK)
@rights_required(rights=["can_manage"])
async def change_role(
    change_role_req: Change_role_req,
    request: Request,
    db: AsyncSession = Depends(get_session),
    auth: AuthJWT = Depends(),
) -> None:
    """Изменение роли."""
    await auth.jwt_required()
    data = jsonable_encoder(change_role_req)
    await change_role_service(data=data, request=request, db=db, auth=auth)


@router.get(
    "/roles", response_model=list[ShowRolesResp], status_code=status.HTTP_200_OK
)
@rights_required(rights=["can_manage"])
async def show_roles(
    request: Request,
    db: AsyncSession = Depends(get_session),
    auth: AuthJWT = Depends(),
) -> list[ShowRolesResp]:
    """Просмотр всех ролей."""
    await auth.jwt_required()
    # получаем роли и формируем из них представление
    roles = await show_roles_service(request=request, db=db, auth=auth)
    return [ShowRolesResp(**role.__dict__) for role in roles]


@router.post("/assign_user_role", status_code=status.HTTP_200_OK)
@rights_required(rights=["can_manage"])
async def assign_user_role(
    assign_user_role_req: Assign_user_role_req,
    request: Request,
    db: AsyncSession = Depends(get_session),
    auth: AuthJWT = Depends(),
) -> None:
    """Назначение роли пользователю."""
    await auth.jwt_required()
    data = jsonable_encoder(assign_user_role_req)
    await assign_user_role_service(data=data, request=request, db=db, auth=auth)


@router.post("/deprive_user_role", status_code=status.HTTP_200_OK)
@rights_required(rights=["can_manage"])
async def deprive_user_role(
    deprive_user_role_req: Deprive_user_role_req,
    request: Request,
    db: AsyncSession = Depends(get_session),
    auth: AuthJWT = Depends(),
) -> None:
    """Лишение пользователя роли."""
    await auth.jwt_required()
    data = jsonable_encoder(deprive_user_role_req)
    await deprive_user_role_service(data=data, request=request, db=db, auth=auth)


@router.post(
    "/show_user_rights",
    response_model=ShowUserRightsResp,
    status_code=status.HTTP_200_OK,
)
@rights_required(rights=["can_manage"])
async def show_user_rights(
    show_user_rights_req: Show_user_rights_req,
    request: Request,
    db: AsyncSession = Depends(get_session),
    auth: AuthJWT = Depends(),
) -> ShowUserRightsResp:
    """Проверка наличия прав у пользователя."""
    await auth.jwt_required()
    data = jsonable_encoder(show_user_rights_req)
    # получаем данные и формируем из них представление
    user_login, role = await show_user_rights_service(
        data=data, request=request, db=db, auth=auth
    )
    if role:
        return ShowUserRightsResp(**role.__dict__, user_login=user_login)
    return ShowUserRightsResp(user_login=user_login)


@router.delete("/delete_test_data", status_code=status.HTTP_200_OK)
async def delete_test_data(
    db: AsyncSession = Depends(get_session),
) -> None:
    """Удаление тестовых данных."""
    # проверяем, включен ли тестовый режим, иначе ошибка
    if not settings.test_mode:
        raise HTTPException(
            status_code=400, detail="Test mode is off. You may not delete test data."
        )

    await delete_test_data_service(db=db)
