"""Read-слой для companies-домена: query-функции + Pydantic view-модели."""
from __future__ import annotations

import datetime
import uuid

import pydantic
import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from app.companies.domain.models import Company


class CompanyView(pydantic.BaseModel):
    """Pydantic read-модель компании для API ответов."""

    model_config = pydantic.ConfigDict(from_attributes=True)

    id: uuid.UUID = pydantic.Field(description="UUID компании")
    name: str = pydantic.Field(description="Название компании")
    created_at: datetime.datetime = pydantic.Field(description="Когда создана")
    updated_at: datetime.datetime = pydantic.Field(description="Когда обновлена в последний раз")


async def get_company_list(*, session: AsyncSession) -> list[CompanyView]:
    """Список всех компаний, отсортированных по дате создания (новые первыми)."""
    stmt = sa.select(Company).order_by(Company.created_at.desc())
    rows = (await session.scalars(stmt)).all()
    return [CompanyView.model_validate(c, from_attributes=True) for c in rows]


async def get_company_view(
    *,
    company_id: uuid.UUID,
    session: AsyncSession,
) -> CompanyView:
    """Получение одной компании по ID. Кидает LookupError если не найдена."""
    stmt = sa.select(Company).where(Company.id == company_id)
    company = await session.scalar(stmt)
    if company is None:
        raise LookupError(f"Company {company_id} not found")
    return CompanyView.model_validate(company, from_attributes=True)
