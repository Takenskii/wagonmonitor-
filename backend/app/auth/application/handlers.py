"""Write-слой для auth-домена: login.

`login` строго говоря не мутирует state, но создаёт JWT-токен, который
имеет внешний эффект (потом используется юзером). Кладём в handlers.
"""
from __future__ import annotations

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from app.companies.domain.models import Company
from app.shared.security import create_access_token, verify_password
from app.users.application.views import UserView, _build_view
from app.users.domain.models import User


class InvalidCredentialsError(Exception):
    """Email не найден ИЛИ пароль не совпадает (не палим что именно)."""


async def login(
    *,
    email: str,
    password: str,
    session: AsyncSession,
) -> tuple[str, UserView]:
    """
    Проверить email + пароль, выдать JWT.

    Returns: (token, UserView)
    Raises: InvalidCredentialsError если email не найден или пароль неверный
    """
    stmt = (
        sa.select(User, Company.name.label("company_name"))
        .join(Company, Company.id == User.company_id)
        .where(User.email == email)
    )
    row = (await session.execute(stmt)).first()
    if row is None:
        raise InvalidCredentialsError("Invalid credentials")
    user, company_name = row
    if not await verify_password(password, user.password_hash):
        raise InvalidCredentialsError("Invalid credentials")

    token = create_access_token(
        user_id=user.id,
        company_id=user.company_id,
        role=user.role.value,
    )
    return token, _build_view(user, company_name)
