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
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_404_NOT_FOUND,
            detail="Company not found",
        )
    return company


@router.post(
    "/",
    summary="Создание компании",
    response_model=CompanyOut,
    status_code=fastapi.status.HTTP_201_CREATED,
    responses={
        201: {"description": "Компания создана"},
        401: {"description": "Не аутентифицирован"},
        403: {"description": "Только для superadmin"},
    },
)
async def create_company(
    req: CompanyCreate,
    _: Superadmin,
    db: Session,
) -> Company:
    """
    Создание новой компании.

    Доступно только superadmin'у. Возвращает созданную компанию.
    """
    company = Company(name=req.name)
    db.add(company)
    await db.commit()
    await db.refresh(company)
    return company


@router.get(
    "/",
    summary="Список компаний",
    response_model=list[CompanyOut],
    status_code=fastapi.status.HTTP_200_OK,
    responses={
        200: {"description": "Список компаний"},
        401: {"description": "Не аутентифицирован"},
        403: {"description": "Только для superadmin"},
    },
)
async def list_companies(_: Superadmin, db: Session) -> list[Company]:
    """
    Получение списка компаний.

    Возвращает все компании, отсортированные по дате создания (новые первыми).
    """
    result = await db.execute(sa.select(Company).order_by(Company.created_at.desc()))
    return list(result.scalars().all())


@router.get(
    "/{company_id}/",
    summary="Получение компании",
    response_model=CompanyOut,
    status_code=fastapi.status.HTTP_200_OK,
    responses={
        200: {"description": "Данные компании"},
        401: {"description": "Не аутентифицирован"},
        403: {"description": "Только для superadmin"},
        404: {"description": "Компания не найдена"},
    },
)
async def get_company(
    company_id: uuid.UUID,
    _: Superadmin,
    db: Session,
) -> Company:
    """
    Получение компании по её ID.

    Возвращает данные компании, если она существует.
    """
    return await _get_or_404(db, company_id)


@router.patch(
    "/{company_id}/",
    summary="Обновление компании",
    response_model=CompanyOut,
    status_code=fastapi.status.HTTP_200_OK,
    responses={
        200: {"description": "Компания обновлена"},
        401: {"description": "Не аутентифицирован"},
        403: {"description": "Только для superadmin"},
        404: {"description": "Компания не найдена"},
    },
)
async def update_company(
    company_id: uuid.UUID,
    req: CompanyUpdate,
    _: Superadmin,
    db: Session,
) -> Company:
    """
    Обновление компании.

    Меняет переданные поля компании. Возвращает актуальную версию.
    """
    company = await _get_or_404(db, company_id)
    if req.name is not None:
        company.name = req.name
    await db.commit()
    await db.refresh(company)
    return company


@router.delete(
    "/{company_id}/",
    summary="Удаление компании",
    status_code=fastapi.status.HTTP_204_NO_CONTENT,
    responses={
        204: {"description": "Компания удалена"},
        401: {"description": "Не аутентифицирован"},
        403: {"description": "Только для superadmin"},
        404: {"description": "Компания не найдена"},
    },
)
async def delete_company(
    company_id: uuid.UUID,
    _: Superadmin,
    db: Session,
) -> fastapi.Response:
    """
    Удаление компании по её ID.

    Каскадно удаляет всех пользователей компании.
    """
    company = await _get_or_404(db, company_id)
    await db.delete(company)
    await db.commit()
    return fastapi.Response(status_code=fastapi.status.HTTP_204_NO_CONTENT)
