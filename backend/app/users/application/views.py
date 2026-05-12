"""Read-слой для users-домена: query-функции + Pydantic view-модели.

Scope:
  - superadmin: все юзеры (опционально фильтр по company_id)
  - admin:      только юзеры своей компании
"""
from __future__ import annotations

import datetime
import uuid

import pydantic
import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from app.companies.domain.models import Company
from app.entrypoints.dependencies import Identity
from app.shared.database.enums import UserRole
from app.users.domain.models import User


class UserView(pydantic.BaseModel):
    """Pydantic read-модель пользователя (с company_name из JOIN)."""

    model_config = pydantic.ConfigDict(from_attributes=True)

    id: uuid.UUID = pydantic.Field(description="UUID пользователя")
    email: pydantic.EmailStr = pydantic.Field(description="Email")
    full_name: str | None = pydantic.Field(default=None, description="ФИО")
    role: UserRole = pydantic.Field(description="Роль в системе")
    company_id: uuid.UUID = pydantic.Field(description="UUID компании")
    company_name: str = pydantic.Field(description="Название компании (денормализовано)")
    created_at: datetime.datetime
    updated_at: datetime.datetime


def can_access(actor: Identity, target_company_id: uuid.UUID) -> bool:
    """Виден ли юзер из target_company_id для actor'а?"""
    return actor.role == UserRole.SUPERADMIN or actor.company_id == target_company_id


def _build_view(user: User, company_name: str) -> UserView:
    return UserView(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        company_id=user.company_id,
        company_name=company_name,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )


async def get_user_list(
    *,
    actor: Identity,
    company_filter: uuid.UUID | None,
    session: AsyncSession,
) -> list[UserView]:
    """
    Список пользователей в scope текущего юзера.

    - superadmin: всех; опционально фильтр по `company_filter`
    - admin: только из своей компании; `company_filter` игнорируется
    """
    stmt = (
        sa.select(User, Company.name.label("company_name"))
        .join(Company, Company.id == User.company_id)
        .order_by(User.created_at.desc())
    )

    if actor.role == UserRole.SUPERADMIN:
        if company_filter is not None:
            stmt = stmt.where(User.company_id == company_filter)
    else:
        stmt = stmt.where(User.company_id == actor.company_id)

    rows = (await session.execute(stmt)).all()
    return [_build_view(u, name) for u, name in rows]


async def get_user_view(
    *,
    user_id: uuid.UUID,
    actor: Identity,
    session: AsyncSession,
) -> UserView:
    """
    Получить одного юзера по ID, с проверкой scope.
    Кидает LookupError если юзер не существует ИЛИ не виден текущему actor'у.
    """
    stmt = (
        sa.select(User, Company.name.label("company_name"))
        .join(Company, Company.id == User.company_id)
        .where(User.id == user_id)
    )
    row = (await session.execute(stmt)).first()
    if row is None:
        raise LookupError(f"User {user_id} not found")
    user, company_name = row
    if not can_access(actor, user.company_id):
        # Не палим что юзер существует — для actor'а его «не существует»
        raise LookupError(f"User {user_id} not found")
    return _build_view(user, company_name)
