"""Admin endpoints for User management.

Scope:
  - superadmin: any user in any company (optional ?company_id= filter)
  - admin:      users in own company only
"""
from __future__ import annotations

import uuid
from typing import Annotated

import fastapi
import sqlalchemy as sa
from sqlalchemy.ext import asyncio as asa

from app.companies.domain.models import Company
from app.entrypoints.dependencies import CompanyAdmin, Identity, Session, Superadmin
from app.entrypoints.schemas.auth import LoginResponse
from app.entrypoints.schemas.users import UserCreate, UserOut, UserUpdate
from app.shared.database.enums import UserRole
from app.shared.security import create_access_token, hash_password
from app.users.domain.models import User

router = fastapi.APIRouter(
    prefix="/api/v1/admin/users",
    tags=["admin:users"],
)


def _can_access(actor: Identity, target_company_id: uuid.UUID) -> bool:
    if actor.role == UserRole.SUPERADMIN:
        return True
    return actor.company_id == target_company_id


async def _get_or_404(db: asa.AsyncSession, user_id: uuid.UUID) -> User:
    result = await db.execute(sa.select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user


@router.post(
    "/",
    summary="Создание пользователя",
    response_model=UserOut,
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
) -> User:
    """
    Создание нового пользователя.

    Superadmin создаёт юзера в любой компании (поле company_id обязательно).
    Admin создаёт юзера только в своей компании (company_id игнорируется).
    """
    if actor.role == UserRole.SUPERADMIN:
        if req.company_id is None:
            raise fastapi.HTTPException(
                status_code=fastapi.status.HTTP_400_BAD_REQUEST,
                detail="company_id is required for superadmin",
            )
        target_company_id = req.company_id
    else:
        target_company_id = actor.company_id

    company_exists = await db.execute(
        sa.select(Company.id).where(Company.id == target_company_id)
    )
    if company_exists.scalar_one_or_none() is None:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_404_NOT_FOUND,
            detail="Company not found",
        )

    if req.role == UserRole.SUPERADMIN and actor.role != UserRole.SUPERADMIN:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_403_FORBIDDEN,
            detail="Only superadmin can grant superadmin role",
        )

    user = User(
        email=req.email,
        password_hash=await hash_password(req.password),
        role=req.role,
        full_name=req.full_name,
        company_id=target_company_id,
    )
    db.add(user)
    try:
        await db.commit()
    except sa.exc.IntegrityError:
        await db.rollback()
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_409_CONFLICT,
            detail="Email already exists",
        ) from None
    await db.refresh(user)
    return user


@router.get(
    "/",
    summary="Список пользователей",
    response_model=list[UserOut],
    status_code=fastapi.status.HTTP_200_OK,
    responses={
        200: {"description": "Список пользователей"},
        401: {"description": "Не аутентифицирован"},
        403: {"description": "Недостаточно прав"},
    },
)
async def list_users(
    actor: CompanyAdmin,
    db: Session,
    company_id: Annotated[uuid.UUID | None, fastapi.Query()] = None,
) -> list[User]:
    """
    Получение списка пользователей.

    Superadmin видит всех; опциональный фильтр ?company_id= ограничивает выборку.
    Admin видит только пользователей своей компании.
    """
    stmt = sa.select(User).order_by(User.created_at.desc())
    if actor.role == UserRole.SUPERADMIN:
        if company_id is not None:
            stmt = stmt.where(User.company_id == company_id)
    else:
        stmt = stmt.where(User.company_id == actor.company_id)
    result = await db.execute(stmt)
    return list(result.scalars().all())


@router.get(
    "/{user_id}/",
    summary="Получение пользователя",
    response_model=UserOut,
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
) -> User:
    """
    Получение пользователя по ID.

    Возвращает пользователя если он в зоне видимости текущего админа.
    """
    user = await _get_or_404(db, user_id)
    if not _can_access(actor, user.company_id):
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user


@router.patch(
    "/{user_id}/",
    summary="Обновление пользователя",
    response_model=UserOut,
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
) -> User:
    """
    Обновление пользователя.

    Меняет переданные поля. Только superadmin может назначить роль superadmin.
    Пароль обновляется только если передан непустой.
    """
    user = await _get_or_404(db, user_id)
    if not _can_access(actor, user.company_id):
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    if req.email is not None:
        user.email = req.email
    if req.full_name is not None:
        user.full_name = req.full_name
    if req.role is not None:
        if req.role == UserRole.SUPERADMIN and actor.role != UserRole.SUPERADMIN:
            raise fastapi.HTTPException(
                status_code=fastapi.status.HTTP_403_FORBIDDEN,
                detail="Only superadmin can grant superadmin role",
            )
        user.role = req.role
    if req.password is not None:
        user.password_hash = await hash_password(req.password)

    try:
        await db.commit()
    except sa.exc.IntegrityError:
        await db.rollback()
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_409_CONFLICT,
            detail="Email already exists",
        ) from None
    await db.refresh(user)
    return user


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
    Удаление пользователя по ID.

    Нельзя удалить самого себя — нужен другой админ для очистки.
    """
    user = await _get_or_404(db, user_id)
    if not _can_access(actor, user.company_id):
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    if user.id == actor.user_id:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete yourself",
        )
    await db.delete(user)
    await db.commit()
    return fastapi.Response(status_code=fastapi.status.HTTP_204_NO_CONTENT)


@router.post(
    "/{user_id}/impersonate/",
    summary="Войти как пользователь",
    response_model=LoginResponse,
    status_code=fastapi.status.HTTP_200_OK,
    responses={
        200: {"description": "Получен JWT-токен от имени указанного пользователя"},
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

    Только для superadmin. Возвращает JWT-токен от имени целевого пользователя
    с маркером `impersonated_by` для audit-трейла.
    """
    result = await db.execute(
        sa.select(User, Company)
        .join(Company, Company.id == User.company_id)
        .where(User.id == user_id)
    )
    row = result.first()
    if row is None:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    target_user, target_company = row

    token = create_access_token(
        user_id=target_user.id,
        company_id=target_company.id,
        role=target_user.role.value,
        impersonated_by=actor.user_id,
    )
    return LoginResponse(
        token=token,
        user_id=target_user.id,
        email=target_user.email,
        full_name=target_user.full_name,
        role=target_user.role,
        company_id=target_company.id,
        company_name=target_company.name,
    )
