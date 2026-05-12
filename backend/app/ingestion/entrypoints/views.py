"""Ingestion endpoint: приём данных о вагонах через JSON."""
from __future__ import annotations

import fastapi

from app.entrypoints.dependencies import Session, Superadmin
from app.entrypoints.schemas.ingestion import IngestRequest, IngestResponse
from app.ingestion.application.handlers import ingest_batch

router = fastapi.APIRouter(prefix="/api/v1/ingestion", tags=["ingestion"])


@router.post(
    "/push/",
    summary="Загрузка данных о вагонах",
    response_model=IngestResponse,
    status_code=fastapi.status.HTTP_201_CREATED,
    responses={
        201: {"description": "Батч обработан"},
        401: {"description": "Не аутентифицирован"},
        403: {"description": "Только для superadmin"},
        413: {"description": "Превышен размер батча"},
    },
)
async def push_wagons(
    req: IngestRequest,
    _: Superadmin,
    db: Session,
) -> IngestResponse:
    """
    Принять список вагонов и записать их в БД.

    Upsert по `wagon_number` — если вагон с таким номером уже есть, его поля
    обновляются (кроме `first_seen` и `created_at`). Иначе создаётся новая запись.

    Принимает поле `wagon_number` (или legacy `vagon_number` для совместимости).

    Только superadmin. Лимит 10 000 вагонов на батч.
    """
    items = [w.model_dump(exclude_unset=False) for w in req.wagons]
    result = await ingest_batch(items, source="api", db=db)
    return IngestResponse(**result)
