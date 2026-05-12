"""Tracking endpoints: assign / remove / move wagons."""
from __future__ import annotations

import fastapi

from app.entrypoints.dependencies import CompanyAdmin, Session
from app.entrypoints.schemas.tracking import (
    AssignRequest,
    AssignResponse,
    MoveRequest,
    MoveResponse,
    RemoveRequest,
    RemoveResponse,
)
from app.tracking.application import handlers
from app.tracking.application.handlers import ConflictError

router = fastapi.APIRouter(prefix="/api/v1/tracking", tags=["tracking"])


@router.post(
    "/assign/",
    summary="Постановка вагонов на слежение",
    response_model=AssignResponse,
    status_code=fastapi.status.HTTP_201_CREATED,
    responses={
        201: {"description": "Вагоны поставлены на слежение"},
        400: {"description": "Неверные параметры (например, group_id и new_group_name вместе)"},
        401: {"description": "Не аутентифицирован"},
        403: {"description": "Недостаточно прав"},
        404: {"description": "Группа не найдена"},
    },
)
async def assign_wagons(
    req: AssignRequest,
    actor: CompanyAdmin,
    db: Session,
) -> AssignResponse:
    """
    Поставить вагон(ы) на слежение в компании текущего actor'а.

    Можно указать существующую группу через `group_id` ИЛИ создать новую через
    `new_group_name`. Можно ни то ни другое — тогда вагоны вне группы.

    Если вагон уже под слежением — обновим параметры и реактивируем (если был снят).
    """
    try:
        result = await handlers.assign_wagons(
            wagon_numbers=req.wagon_numbers,
            actor=actor,
            session=db,
            group_id=req.group_id,
            new_group_name=req.new_group_name,
            initial_territory=req.initial_territory,
            remove_on_route_end=req.remove_on_route_end,
            deferred_start_at=req.deferred_start_at,
            auto_remove_at=req.auto_remove_at,
        )
    except ConflictError as e:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_400_BAD_REQUEST, detail=str(e)
        ) from None
    except LookupError as e:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_404_NOT_FOUND, detail=str(e)
        ) from None

    return AssignResponse(**result)


@router.post(
    "/remove/",
    summary="Снятие вагонов со слежения",
    response_model=RemoveResponse,
    status_code=fastapi.status.HTTP_200_OK,
    responses={
        200: {"description": "Вагоны сняты со слежения"},
        401: {"description": "Не аутентифицирован"},
        403: {"description": "Недостаточно прав"},
    },
)
async def remove_wagons(
    req: RemoveRequest,
    actor: CompanyAdmin,
    db: Session,
) -> RemoveResponse:
    """
    Снять вагон(ы) со слежения у компании текущего actor'а.

    Soft-delete: `active=false, removed_at=now`. Вагоны которые не были активны
    или отсутствовали в слежении — попадают в `not_found`.
    """
    result = await handlers.remove_wagons(
        wagon_numbers=req.wagon_numbers,
        actor=actor,
        session=db,
    )
    return RemoveResponse(**result)


@router.post(
    "/move/",
    summary="Перемещение вагонов между группами",
    response_model=MoveResponse,
    status_code=fastapi.status.HTTP_200_OK,
    responses={
        200: {"description": "Вагоны перемещены"},
        400: {"description": "Конфликт параметров"},
        401: {"description": "Не аутентифицирован"},
        403: {"description": "Недостаточно прав"},
        404: {"description": "Группа не найдена"},
    },
)
async def move_wagons(
    req: MoveRequest,
    actor: CompanyAdmin,
    db: Session,
) -> MoveResponse:
    """
    Переместить вагон(ы) в другую группу (или вне групп).

    Можно указать `group_id` существующей группы ИЛИ `new_group_name` для
    создания новой. `group_id=null` без `new_group_name` — вынуть из групп.
    """
    try:
        result = await handlers.move_wagons(
            wagon_numbers=req.wagon_numbers,
            actor=actor,
            session=db,
            group_id=req.group_id,
            new_group_name=req.new_group_name,
        )
    except ConflictError as e:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_400_BAD_REQUEST, detail=str(e)
        ) from None
    except LookupError as e:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_404_NOT_FOUND, detail=str(e)
        ) from None

    return MoveResponse(**result)
