"""Pydantic schemas for ingestion endpoint.

Принимаем 62 поля вагона + бизнес-идентификатор `wagon_number`.
Все кроме `wagon_number` — опциональные (источник может прислать частичные данные).

Поддерживаем оба формата идентификатора через `AliasChoices`:
  - `wagon_number` (новый, без опечатки)
  - `vagon_number` (легаси из КТЖ / v1)
"""
from __future__ import annotations

import datetime

import pydantic


class WagonIngestItem(pydantic.BaseModel):
    """Один вагон в payload'е ingestion'а."""

    model_config = pydantic.ConfigDict(
        populate_by_name=True,
        # Лишние поля не должны валить запрос — могут быть кастомные колонки и т.п.
        extra="allow",
    )

    # Идентификатор — принимаем оба написания (legacy `vagon_number`)
    number: str = pydantic.Field(
        validation_alias=pydantic.AliasChoices("wagon_number", "vagon_number", "number"),
        serialization_alias="wagon_number",
        max_length=20,
    )

    # ── Состояние ─────────────────────────────────────────────────────────────
    is_full_name: str | None = None
    doc_number: str | None = None

    # ── Погрузка/выгрузка ─────────────────────────────────────────────────────
    loading_date: datetime.datetime | None = None
    loading_station: str | None = None
    loading_station_name: str | None = None
    loading_rw_name: str | None = None
    loading_country_name: str | None = None

    # ── Дислокация ────────────────────────────────────────────────────────────
    disl_rw: str | None = None
    disl_rw_name: str | None = None
    disl_country_name: str | None = None

    # ── Операция ──────────────────────────────────────────────────────────────
    oper_station: str | None = None
    oper_station_name: str | None = None
    oper_station_department: str | None = None
    oper_code: str | None = None
    oper_name: str | None = None
    oper_full_name: str | None = None
    oper_date: datetime.datetime | None = None

    # ── Груз ──────────────────────────────────────────────────────────────────
    cargo_weight: float | None = None
    cargo_code: str | None = None
    cargo_name: str | None = None
    cargo_full_name: str | None = None

    # ── Поезд ─────────────────────────────────────────────────────────────────
    train_num: str | None = None
    train_index: str | None = None
    train_index_1: str | None = None
    train_index_2: str | None = None
    train_index_3: str | None = None
    npp: str | None = None
    train_from_station_name: str | None = None
    train_to_station_name: str | None = None
    car_number: str | None = None

    # ── Назначение ────────────────────────────────────────────────────────────
    dest_rw: str | None = None
    dest_rw_name: str | None = None
    dest_country_name: str | None = None
    dest_station: str | None = None
    dest_station_name: str | None = None
    dest_station_department: str | None = None
    delivery_date: datetime.date | None = None
    rest_distance: float | None = None
    rest_run: float | None = None

    # ── Получатель / Отправитель ──────────────────────────────────────────────
    grpol_okpo: str | None = None
    grpol_name: str | None = None
    grpol_rw: str | None = None
    grotpr_okpo: str | None = None
    grotpr_name: str | None = None
    grotpr_rw: str | None = None

    # ── Источник данных ───────────────────────────────────────────────────────
    rash_rw: str | None = None
    rash_date: datetime.datetime | None = None

    # ── Стоянка / счётчики ────────────────────────────────────────────────────
    start_date_on_station: datetime.datetime | None = None
    day_count_on_station: float | None = None
    days_wo_operation: float | None = None
    days_from_start: float | None = None
    days_on_trade_union: float | None = None
    cl_start_at: datetime.datetime | None = None

    # ── Неисправности ─────────────────────────────────────────────────────────
    faulty_name: str | None = None

    # ── Техпаспорт ────────────────────────────────────────────────────────────
    car_type_name: str | None = None
    date_build: datetime.date | None = None
    capacity: float | None = None
    volume: float | None = None
    extended_life_time: datetime.date | None = None
    date_plan_repair: datetime.date | None = None

    # ── НСП ───────────────────────────────────────────────────────────────────
    nsp_indicator: str | None = None


class IngestRequest(pydantic.BaseModel):
    """Payload для POST /ingestion/push/."""

    wagons: list[WagonIngestItem] = pydantic.Field(min_length=1, max_length=10_000)


class IngestResponse(pydantic.BaseModel):
    """Результат ingestion-батча."""

    wagons_total: int
    wagons_updated: int
    errors: int
