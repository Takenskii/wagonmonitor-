"""Admin endpoints for Company management. Superadmin only."""
from __future__ import annotations

import uuid

import fastapi
import sqlalchemy as sa
from sqlalchemy.ext import asyncio as asa

from app.companies.domain.models import Company
from app.entrypoints.dependencies import Session, Superadmin
from app.entrypoints.schemas.companies import CompanyCreate, CompanyOut, CompanyUpdate

router = fastapi.APIRouter(
    prefix="/api/v1/admin/companies",
    tags=["admin:companies"],
)


async def _get_or_404(db: asa.AsyncSession, company_id: uuid.UUID) -> Company:
    result = await db.execute(sa.select(Company).where(Company.id == company_id))
    company = result.scalar_one_or_none()
    if company is None:
        raise fastapi.HTTPException(status_code=404, detail="Company not found")
    return company


@router.post("", response_model=CompanyOut, status_code=201)
async def create_company(req: CompanyCreate, _: Superadmin, db: Session) -> Company:
    company = Company(name=req.name)
    db.add(company)
    await db.commit()
    await db.refresh(company)
    return company


@router.get("", response_model=list[CompanyOut])
async def list_companies(_: Superadmin, db: Session) -> list[Company]:
    result = await db.execute(sa.select(Company).order_by(Company.created_at.desc()))
    return list(result.scalars().all())


@router.get("/{company_id}", response_model=CompanyOut)
async def get_company(company_id: uuid.UUID, _: Superadmin, db: Session) -> Company:
    return await _get_or_404(db, company_id)


@router.patch("/{company_id}", response_model=CompanyOut)
async def update_company(
    company_id: uuid.UUID,
    req: CompanyUpdate,
    _: Superadmin,
    db: Session,
) -> Company:
    company = await _get_or_404(db, company_id)
    if req.name is not None:
        company.name = req.name
    await db.commit()
    await db.refresh(company)
    return company


@router.delete("/{company_id}", status_code=204)
async def delete_company(company_id: uuid.UUID, _: Superadmin, db: Session) -> None:
    company = await _get_or_404(db, company_id)
    await db.delete(company)
    await db.commit()
