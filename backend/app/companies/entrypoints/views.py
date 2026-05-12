"""Admin endpoints for Company management. Superadmin only."""
from __future__ import annotations

import uuid

import fastapi

from app.companies.application import handlers, views
from app.companies.application.views import CompanyView
from app.entrypoints.dependencies import Session, Superadmin
from app.entrypoints.schemas.companies import CompanyCreate, CompanyUpdate

router = fastapi.APIRouter(
    prefix="/api/v1/admin/companies",
    tags=["admin:companies"],
)


@router.post(
    "/",
    summary="Создание компании",
    response_model=CompanyView,
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
) -> CompanyView:
    """
    Создание новой компании.

    Доступно только superadmin'у. Возвращает созданную компанию.
    """
    return await handlers.create_company(name=req.name, session=db)


@router.get(
    "/",
    summary="Список компаний",
    response_model=list[CompanyView],
    status_code=fastapi.status.HTTP_200_OK,
    responses={
        200: {"description": "Список компаний"},
        401: {"description": "Не аутентифицирован"},
        403: {"description": "Только для superadmin"},
    },
)
async def list_companies(_: Superadmin, db: Session) -> list[CompanyView]:
    """
    Получение списка компаний.

    Возвращает все компании, отсортированные по дате создания (новые первыми).
    """
    return await views.get_company_list(session=db)


@router.get(
    "/{company_id}/",
    summary="Получение компании",
    response_model=CompanyView,
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
) -> CompanyView:
    """
    Получение компании по её ID.
    """
    try:
        return await views.get_company_view(company_id=company_id, session=db)
    except LookupError:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_404_NOT_FOUND,
            detail="Company not found",
        ) from None


@router.patch(
    "/{company_id}/",
    summary="Обновление компании",
    response_model=CompanyView,
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
) -> CompanyView:
    """
    Обновление компании.

    Меняет переданные поля. Возвращает актуальную версию.
    """
    try:
        return await handlers.update_company(
            company_id=company_id,
            name=req.name,
            session=db,
        )
    except LookupError:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_404_NOT_FOUND,
            detail="Company not found",
        ) from None


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
    Удаление компании по ID.

    Каскадно удаляет всех пользователей компании.
    """
    try:
        await handlers.delete_company(company_id=company_id, session=db)
    except LookupError:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_404_NOT_FOUND,
            detail="Company not found",
        ) from None
    return fastapi.Response(status_code=fastapi.status.HTTP_204_NO_CONTENT)
