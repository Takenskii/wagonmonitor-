"""Write-слой для companies-домена: create / update / delete."""
from __future__ import annotations

import uuid

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from app.companies.application.views import CompanyView
from app.companies.domain.models import Company


async def create_company(
    *,
    name: str,
    session: AsyncSession,
) -> CompanyView:
    """Создать новую компанию."""
    company = Company(name=name)
    session.add(company)
    await session.commit()
    await session.refresh(company)
    return CompanyView.model_validate(company, from_attributes=True)


async def update_company(
    *,
    company_id: uuid.UUID,
    name: str | None,
    session: AsyncSession,
) -> CompanyView:
    """Обновить компанию. Кидает LookupError если не найдена."""
    stmt = sa.select(Company).where(Company.id == company_id)
    company = await session.scalar(stmt)
    if company is None:
        raise LookupError(f"Company {company_id} not found")

    if name is not None:
        company.name = name

    await session.commit()
    await session.refresh(company)
    return CompanyView.model_validate(company, from_attributes=True)


async def delete_company(
    *,
    company_id: uuid.UUID,
    session: AsyncSession,
) -> None:
    """Удалить компанию. Кидает LookupError если не найдена."""
    stmt = sa.select(Company).where(Company.id == company_id)
    company = await session.scalar(stmt)
    if company is None:
        raise LookupError(f"Company {company_id} not found")
    await session.delete(company)
    await session.commit()
