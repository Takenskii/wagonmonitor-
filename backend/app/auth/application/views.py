"""Read-слой для auth-домена."""
from __future__ import annotations

import uuid

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from app.companies.domain.models import Company
from app.users.application.views import UserView, _build_view
from app.users.domain.models import User


async def get_me_view(
    *,
    user_id: uuid.UUID,
    session: AsyncSession,
) -> UserView:
    """
    Получить данные текущего юзера (по user_id из JWT).
    Кидает LookupError если юзер удалён (теоретический случай — JWT валидный, но юзера нет).
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
    return _build_view(user, company_name)
