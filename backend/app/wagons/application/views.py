"""Read-слой для wagons-домена: query-функции + Pydantic view-модели.

Возвращает денормализованные данные для UI: вагон + tracking + group_name в одном объекте.
"""
from __future__ import annotations

import datetime
import uuid
from typing import Literal

import pydantic
import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from app.groups.domain.models import WagonGroup
from app.tracking.domain.models import TrackingAssignment
from app.wagons.domain.models import Wagon


class WagonDislocation(pydantic.BaseModel):
    """Денормализованный вагон для страницы «Слежение»: tracking + (опционально) данные вагона.

    Если вагон ещё не был получен через ingestion (компания поставила его на слежение
    раньше) — все wagon-поля приходят как None. Запись всё равно показывается
    в UI как «ожидает дислокации».
    """

    model_config = pydantic.ConfigDict(from_attributes=True)

    # ── Идентификаторы (всегда из tracking_assignment) ────────────────────────
    track_id: uuid.UUID = pydantic.Field(description="ID записи tracking_assignment")
    number: str = pydantic.Field(description="Номер вагона/контейнера")

    # ── Tracking-инфа ─────────────────────────────────────────────────────────
    group_id: uuid.UUID | None = pydantic.Field(default=None, description="ID группы")
    group_name: str | None = pydantic.Field(default=None, description="Название группы")
    active: bool = pydantic.Field(description="Активно ли слежение")
    removed_at: datetime.datetime | None = pydantic.Field(default=None)

    # ── Wagon-инфа (None если вагон ещё не пришёл через ingestion) ────────────
    wagon_id: uuid.UUID | None = pydantic.Field(default=None, description="UUID вагона в нашей БД")
    first_seen: datetime.datetime | None = None
    last_seen: datetime.datetime | None = None
    last_source: str | None = None

    # ── Все остальные поля вагона ─────────────────────────────────────────────
    is_full_name: str | None = None
    doc_number: str | None = None

    loading_date: datetime.datetime | None = None
    loading_station: str | None = None
    loading_station_name: str | None = None
    loading_rw_name: str | None = None
    loading_country_name: str | None = None

    disl_rw: str | None = None
    disl_rw_name: str | None = None
    disl_country_name: str | None = None

    oper_station: str | None = None
    oper_station_name: str | None = None
    oper_station_department: str | None = None
    oper_code: str | None = None
    oper_name: str | None = None
    oper_full_name: str | None = None
    oper_date: datetime.datetime | None = None

    cargo_weight: float | None = None
    cargo_code: str | None = None
    cargo_name: str | None = None
    cargo_full_name: str | None = None

    train_num: str | None = None
    train_index: str | None = None
    train_index_1: str | None = None
    train_index_2: str | None = None
    train_index_3: str | None = None
    npp: str | None = None
    train_from_station_name: str | None = None
    train_to_station_name: str | None = None
    car_number: str | None = None

    dest_rw: str | None = None
    dest_rw_name: str | None = None
    dest_country_name: str | None = None
    dest_station: str | None = None
    dest_station_name: str | None = None
    dest_station_department: str | None = None
    delivery_date: datetime.date | None = None
    rest_distance: float | None = None
    rest_run: float | None = None

    grpol_okpo: str | None = None
    grpol_name: str | None = None
    grpol_rw: str | None = None
    grotpr_okpo: str | None = None
    grotpr_name: str | None = None
    grotpr_rw: str | None = None

    rash_rw: str | None = None
    rash_date: datetime.datetime | None = None

    start_date_on_station: datetime.datetime | None = None
    day_count_on_station: float | None = None
    days_wo_operation: float | None = None
    days_from_start: float | None = None
    days_on_trade_union: float | None = None
    cl_start_at: datetime.datetime | None = None

    faulty_name: str | None = None

    car_type_name: str | None = None
    date_build: datetime.date | None = None
    capacity: float | None = None
    volume: float | None = None
    extended_life_time: datetime.date | None = None
    date_plan_repair: datetime.date | None = None

    nsp_indicator: str | None = None


# Wagon-колонки которые попадают в выход (без служебных и без id/number — их мы
# заполняем явно: number — из tracking_assignment, id — как wagon_id если есть).
_WAGON_FIELDS = {c.name for c in Wagon.__table__.columns} - {
    "pk", "created_at", "updated_at", "raw_data", "id", "number",
}


def _build_view(
    ta: TrackingAssignment,
    wagon: Wagon | None,
    group: WagonGroup | None,
) -> WagonDislocation:
    """Собрать денормализованный WagonDislocation. wagon=None если ещё не пришёл через ingestion."""
    wagon_data: dict = {}
    if wagon is not None:
        wagon_data = {name: getattr(wagon, name) for name in _WAGON_FIELDS}
        wagon_data["wagon_id"] = wagon.id

    return WagonDislocation(
        track_id=ta.id,
        number=ta.wagon_number,
        group_id=ta.group_id,
        group_name=group.name if group is not None else None,
        active=ta.active,
        removed_at=ta.removed_at,
        **wagon_data,
    )


async def get_dislocation_list(
    *,
    company_id: uuid.UUID,
    session: AsyncSession,
    group_id: uuid.UUID | None = None,
    status: Literal["active", "archived", "all"] = "active",
    search: str | None = None,
) -> list[WagonDislocation]:
    """
    Список вагонов на слежении у компании.

    Идём ОТ tracking_assignments, LEFT JOIN'им wagons и wagon_groups —
    показываем и те ряды, для которых вагон ещё не пришёл через ingestion.
    """
    stmt = (
        sa.select(TrackingAssignment, Wagon, WagonGroup)
        .outerjoin(Wagon, Wagon.number == TrackingAssignment.wagon_number)
        .outerjoin(WagonGroup, WagonGroup.id == TrackingAssignment.group_id)
        .where(TrackingAssignment.company_id == company_id)
        .order_by(TrackingAssignment.wagon_number)
    )

    if status == "active":
        stmt = stmt.where(TrackingAssignment.active.is_(True))
    elif status == "archived":
        stmt = stmt.where(TrackingAssignment.active.is_(False))

    if group_id is not None:
        stmt = stmt.where(TrackingAssignment.group_id == group_id)

    if search:
        stmt = stmt.where(TrackingAssignment.wagon_number.ilike(f"%{search}%"))

    rows = (await session.execute(stmt)).all()
    return [_build_view(ta, w, g) for ta, w, g in rows]
