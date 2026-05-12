"""Dislocation endpoint: список вагонов на слежении у текущей компании."""
from __future__ import annotations

import uuid
from typing import Annotated, Literal

import fastapi

from app.entrypoints.dependencies import CurrentUser, Session
from app.wagons.application.views import WagonDislocation, get_dislocation_list

router = fastapi.APIRouter(prefix="/api/v1/dislocations", tags=["dislocations"])


@router.get(
    "/",
    summary="Список вагонов на слежении",
    response_model=list[WagonDislocation],
    status_code=fastapi.status.HTTP_200_OK,
    responses={
        200: {"description": "Список вагонов с tracking-полями"},
        401: {"description": "Не аутентифицирован"},
    },
)
async def list_dislocations(
    current: CurrentUser,
    db: Session,
    group_id: Annotated[uuid.UUID | None, fastapi.Query()] = None,
    status: Annotated[
        Literal["active", "archived", "all"],
        fastapi.Query(),
    ] = "active",
    search: Annotated[str | None, fastapi.Query(max_length=64)] = None,
) -> list[WagonDislocation]:
    """
    Дислокация — вагоны на слежении у компании текущего юзера.

    Фильтры:
      - `status=active|archived|all` — слежение активно / снято / всё
      - `group_id=<uuid>` — только вагоны в указанной группе
      - `search=<text>` — поиск по номеру вагона (ilike)

    Возвращает денормализованные данные: поля вагона + tracking-инфо
    (`track_id`, `group_id`, `group_name`, `active`).
    """
    return await get_dislocation_list(
        company_id=current.company_id,
        session=db,
        group_id=group_id,
        status=status,
        search=search,
    )
