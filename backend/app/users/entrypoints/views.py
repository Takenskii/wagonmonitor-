"""Admin endpoints for User management."""
from __future__ import annotations

import uuid
from typing import Annotated

import fastapi

from app.entrypoints.dependencies import CompanyAdmin, Session, Superadmin
from app.entrypoints.schemas.auth import LoginResponse
from app.entrypoints.schemas.users import UserCreate, UserUpdate
from app.users.application import handlers, views
from app.users.application.handlers import ConflictError, PermissionError_
from app.users.application.views import UserView

router = fastapi.APIRouter(
    prefix="/api/v1/admin/users",
    tags=["admin:users"],
)


@router.post(
    "/",
    summary="Создание пользователя",
    response_model=UserView,
    status_code=fastapi.status.HTTP_201_CREATED,
    responses={
        201: {"description": "Пользователь создан"},
        400: {"description": "Некорректные данные"},
        401: {"description": "Не аутентифицирован"},
        403: {"description": "Недостаточно прав"},
        404: {"description": "Компания не найдена"},
        409: {"description": "Email уже занят"},
    },
)
async def create_user(
    req: UserCreate,
    actor: CompanyAdmin,
    db: Session,
) -> UserView:
    """
    Создание нового пользователя.

    Superadmin создаёт в любой компании (обязательно `company_id`).
    Admin создаёт только в своей компании (`company_id` игнорируется).
    Только superadmin может назначить роль `superadmin`.
    """
    try:
        return await handlers.create_user(
            email=req.email,
            password=req.password,
            role=req.role,
            full_name=req.full_name,
            company_id=req.company_id,
            actor=actor,
            session=db,
        )
    except ValueError as e:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_400_BAD_REQUEST, detail=str(e)
        ) from None
    except LookupError:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_404_NOT_FOUND, detail="Company not found"
        ) from None
    except PermissionError_ as e:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_403_FORBIDDEN, detail=str(e)
        ) from None
    except ConflictError as e:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_409_CONFLICT, detail=str(e)
        ) from None


@router.get(
    "/",
    summary="Список пользователей",
    response_model=list[UserView],
    status_code=fastapi.status.HTTP_200_OK,
    responses={
        200: {"description": "Список пользователей в scope текущего юзера"},
        401: {"description": "Не аутентифицирован"},
        403: {"description": "Недостаточно прав"},
    },
)
async def list_users(
    actor: CompanyAdmin,
    db: Session,
    company_id: Annotated[uuid.UUID | None, fastapi.Query()] = None,
) -> list[UserView]:
    """
    Получение списка пользователей.

    Superadmin видит всех; `?company_id=` опционально фильтрует.
    Admin видит только пользователей своей компании.
    """
    return await views.get_user_list(
        actor=actor,
        company_filter=company_id,
        session=db,
    )


@router.get(
    "/{user_id}/",
    summary="Получение пользователя",
    response_model=UserView,
    status_code=fastapi.status.HTTP_200_OK,
    responses={
        200: {"description": "Данные пользователя"},
        401: {"description": "Не аутентифицирован"},
        403: {"description": "Недостаточно прав"},
        404: {"description": "Пользователь не найден"},
    },
)
async def get_user(
    user_id: uuid.UUID,
    actor: CompanyAdmin,
    db: Session,
) -> UserView:
    """Получить пользователя по ID (с проверкой scope)."""
    try:
        return await views.get_user_view(user_id=user_id, actor=actor, session=db)
    except LookupError:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_404_NOT_FOUND, detail="User not found"
        ) from None


@router.patch(
    "/{user_id}/",
    summary="Обновление пользователя",
    response_model=UserView,
    status_code=fastapi.status.HTTP_200_OK,
    responses={
        200: {"description": "Пользователь обновлён"},
        401: {"description": "Не аутентифицирован"},
        403: {"description": "Недостаточно прав"},
        404: {"description": "Пользователь не найден"},
        409: {"description": "Email уже занят"},
    },
)
async def update_user(
    user_id: uuid.UUID,
    req: UserUpdate,
    actor: CompanyAdmin,
    db: Session,
) -> UserView:
    """
    Обновить пользователя.

    Меняет переданные поля. Роль superadmin может назначить только superadmin.
    Пароль обновляется только если передан.
    """
    try:
        return await handlers.update_user(
            user_id=user_id,
            email=req.email,
            password=req.password,
            role=req.role,
            full_name=req.full_name,
            actor=actor,
            session=db,
        )
    except LookupError:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_404_NOT_FOUND, detail="User not found"
        ) from None
    except PermissionError_ as e:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_403_FORBIDDEN, detail=str(e)
        ) from None
    except ConflictError as e:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_409_CONFLICT, detail=str(e)
        ) from None


@router.delete(
    "/{user_id}/",
    summary="Удаление пользователя",
    status_code=fastapi.status.HTTP_204_NO_CONTENT,
    responses={
        204: {"description": "Пользователь удалён"},
        400: {"description": "Нельзя удалить себя"},
        401: {"description": "Не аутентифицирован"},
        403: {"description": "Недостаточно прав"},
        404: {"description": "Пользователь не найден"},
    },
)
async def delete_user(
    user_id: uuid.UUID,
    actor: CompanyAdmin,
    db: Session,
) -> fastapi.Response:
    """
    Удалить пользователя по ID.
    Нельзя удалить самого себя.
    """
    try:
        await handlers.delete_user(user_id=user_id, actor=actor, session=db)
    except LookupError:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_404_NOT_FOUND, detail="User not found"
        ) from None
    except PermissionError_ as e:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_400_BAD_REQUEST, detail=str(e)
        ) from None
    return fastapi.Response(status_code=fastapi.status.HTTP_204_NO_CONTENT)


@router.post(
    "/{user_id}/impersonate/",
    summary="Войти как пользователь",
    response_model=LoginResponse,
    status_code=fastapi.status.HTTP_200_OK,
    responses={
        200: {"description": "JWT-токен от имени указанного пользователя"},
        401: {"description": "Не аутентифицирован"},
        403: {"description": "Только для superadmin"},
        404: {"description": "Пользователь не найден"},
    },
)
async def impersonate_user(
    user_id: uuid.UUID,
    actor: Superadmin,
    db: Session,
) -> LoginResponse:
    """
    Имперсонификация: вход за указанного пользователя.

    Только для superadmin. Возвращает JWT-токен с маркером `impersonated_by`
    для audit-трейла.
    """
    try:
        token, user_view = await handlers.impersonate_user(
            user_id=user_id, actor=actor, session=db,
        )
    except LookupError:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_404_NOT_FOUND, detail="User not found"
        ) from None

    return LoginResponse(
        token=token,
        user_id=user_view.id,
        email=user_view.email,
        full_name=user_view.full_name,
        role=user_view.role,
        company_id=user_view.company_id,
        company_name=user_view.company_name,
    )
