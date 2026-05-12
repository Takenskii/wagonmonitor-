"""Write-слой для users-домена: create / update / delete / impersonate.

Все handler'ы принимают `actor: Identity` (текущий пользователь) и решают
правила доступа внутри:
  - superadmin создаёт юзеров в любой компании
  - admin создаёт только в своей компании
  - роль superadmin может выдать только superadmin
  - нельзя удалить самого себя
"""
from __future__ import annotations

import uuid

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from app.companies.domain.models import Company
from app.entrypoints.dependencies import Identity
from app.shared.database.enums import UserRole
from app.shared.security import create_access_token, hash_password
from app.users.application.views import UserView, _build_view, can_access
from app.users.domain.models import User


class PermissionError_(Exception):
    """Действие запрещено правилами доступа."""


class ConflictError(Exception):
    """Нарушение уникальности (например email уже занят)."""


async def _load_with_company(
    *,
    user_id: uuid.UUID,
    session: AsyncSession,
) -> tuple[User, str]:
    """Достать User + название его компании одним запросом. LookupError если нет."""
    stmt = (
        sa.select(User, Company.name.label("company_name"))
        .join(Company, Company.id == User.company_id)
        .where(User.id == user_id)
    )
    row = (await session.execute(stmt)).first()
    if row is None:
        raise LookupError(f"User {user_id} not found")
    return row


async def create_user(
    *,
    email: str,
    password: str,
    role: UserRole,
    full_name: str | None,
    company_id: uuid.UUID | None,
    actor: Identity,
    session: AsyncSession,
) -> UserView:
    """
    Создать нового пользователя.

    Resolve target company:
      - superadmin: использует переданный company_id (обязательно)
      - admin: использует свою компанию; company_id игнорируется

    Только superadmin может выдать роль superadmin.
    """
    if actor.role == UserRole.SUPERADMIN:
        if company_id is None:
            raise ValueError("company_id is required for superadmin")
        target_company_id = company_id
    else:
        target_company_id = actor.company_id

    # Проверка существования компании
    company_stmt = sa.select(Company).where(Company.id == target_company_id)
    company = await session.scalar(company_stmt)
    if company is None:
        raise LookupError(f"Company {target_company_id} not found")

    # Запрет на role escalation
    if role == UserRole.SUPERADMIN and actor.role != UserRole.SUPERADMIN:
        raise PermissionError_("Only superadmin can grant superadmin role")

    user = User(
        email=email,
        password_hash=await hash_password(password),
        role=role,
        full_name=full_name,
        company_id=target_company_id,
    )
    session.add(user)
    try:
        await session.commit()
    except sa.exc.IntegrityError:
        await session.rollback()
        raise ConflictError("Email already exists") from None
    await session.refresh(user)
    return _build_view(user, company.name)


async def update_user(
    *,
    user_id: uuid.UUID,
    email: str | None,
    password: str | None,
    role: UserRole | None,
    full_name: str | None,
    actor: Identity,
    session: AsyncSession,
) -> UserView:
    """
    Обновить пользователя.

    Сохраняет проверку scope (admin → только своя компания), запрет на эскалацию
    в superadmin от не-superadmin'а.
    """
    user, company_name = await _load_with_company(user_id=user_id, session=session)
    if not can_access(actor, user.company_id):
        raise LookupError(f"User {user_id} not found")

    if role is not None:
        if role == UserRole.SUPERADMIN and actor.role != UserRole.SUPERADMIN:
            raise PermissionError_("Only superadmin can grant superadmin role")
        user.role = role

    if email is not None:
        user.email = email
    if full_name is not None:
        user.full_name = full_name
    if password is not None:
        user.password_hash = await hash_password(password)

    try:
        await session.commit()
    except sa.exc.IntegrityError:
        await session.rollback()
        raise ConflictError("Email already exists") from None
    await session.refresh(user)
    return _build_view(user, company_name)


async def delete_user(
    *,
    user_id: uuid.UUID,
    actor: Identity,
    session: AsyncSession,
) -> None:
    """
    Удалить пользователя. Нельзя удалить самого себя.
    """
    stmt = sa.select(User).where(User.id == user_id)
    user = await session.scalar(stmt)
    if user is None:
        raise LookupError(f"User {user_id} not found")
    if not can_access(actor, user.company_id):
        raise LookupError(f"User {user_id} not found")
    if user.id == actor.user_id:
        raise PermissionError_("Cannot delete yourself")
    await session.delete(user)
    await session.commit()


async def impersonate_user(
    *,
    user_id: uuid.UUID,
    actor: Identity,
    session: AsyncSession,
) -> tuple[str, UserView]:
    """
    Выписать JWT-токен от имени указанного пользователя.
    Только superadmin (проверяется на entrypoint-уровне через `Superadmin` dep).

    Returns: (token, UserView)
    """
    user, company_name = await _load_with_company(user_id=user_id, session=session)
    token = create_access_token(
        user_id=user.id,
        company_id=user.company_id,
        role=user.role.value,
        impersonated_by=actor.user_id,
    )
    return token, _build_view(user, company_name)
