"""Wagon — центральная сущность с текущей дислокацией.

Объединяет анкор-данные (когда впервые увидели, источник) и поля дислокации
из ГВЦ КТЖ (~62 поля по паритету с wagonmonitor.kz). Один ряд на номер вагона.

Идентификация:
  - `pk:int` и `id:UUID` — техническая, от Base
  - `number:VARCHAR(20) UNIQUE` — бизнес-идентификатор. Для контейнеров формат `GLLU9133332`.
"""
from __future__ import annotations

import datetime

import sqlalchemy as sa
from sqlalchemy import orm
from sqlalchemy.dialects.postgresql import JSONB

from app.shared.database.base import Base


class Wagon(Base):
    __tablename__ = "wagons"

    number: orm.Mapped[str] = orm.mapped_column(
        sa.String(20),
        unique=True,
        nullable=False,
        index=True,
        comment="Номер вагона / контейнера",
    )

    # ── Анкор-инфа (когда видели) ─────────────────────────────────────────────
    first_seen: orm.Mapped[datetime.datetime] = orm.mapped_column(
        sa.DateTime(timezone=True),
        comment="Когда впервые увидели этот вагон в наших данных",
    )
    last_seen: orm.Mapped[datetime.datetime] = orm.mapped_column(
        sa.DateTime(timezone=True),
        comment="Когда последний раз обновляли данные дислокации",
    )
    last_source: orm.Mapped[str | None] = orm.mapped_column(
        sa.String(20),
        comment="Источник последнего обновления: api / ftp / manual",
    )

    # ── Состояние ─────────────────────────────────────────────────────────────
    is_full_name: orm.Mapped[str | None] = orm.mapped_column(
        sa.String(20),
        comment="Груж/Пор",
    )
    doc_number: orm.Mapped[str | None] = orm.mapped_column(
        sa.String(50),
        comment="Номер накладной",
    )

    # ── Погрузка/выгрузка ─────────────────────────────────────────────────────
    loading_date: orm.Mapped[datetime.datetime | None] = orm.mapped_column(
        sa.DateTime(timezone=True),
        comment="Дата погрузки/выгрузки",
    )
    loading_station: orm.Mapped[str | None] = orm.mapped_column(
        sa.String(20),
        comment="Код станции погрузки/выгрузки",
    )
    loading_station_name: orm.Mapped[str | None] = orm.mapped_column(
        sa.String(255),
        comment="Станция погрузки/выгрузки",
    )
    loading_rw_name: orm.Mapped[str | None] = orm.mapped_column(
        sa.String(100),
        comment="Дорога погрузки/выгрузки",
    )
    loading_country_name: orm.Mapped[str | None] = orm.mapped_column(
        sa.String(100),
        comment="ЖД администрация ст. погрузки/выгрузки",
    )

    # ── Дислокация ────────────────────────────────────────────────────────────
    disl_rw: orm.Mapped[str | None] = orm.mapped_column(
        sa.String(20),
        comment="Код дороги дислокации",
    )
    disl_rw_name: orm.Mapped[str | None] = orm.mapped_column(
        sa.String(100),
        comment="Дорога дислокации",
    )
    disl_country_name: orm.Mapped[str | None] = orm.mapped_column(
        sa.String(100),
        comment="ЖД администрация дислокации",
    )

    # ── Операция ──────────────────────────────────────────────────────────────
    oper_station: orm.Mapped[str | None] = orm.mapped_column(
        sa.String(20),
        comment="Код станции операции",
    )
    oper_station_name: orm.Mapped[str | None] = orm.mapped_column(
        sa.String(255),
        comment="Станция операции",
    )
    oper_station_department: orm.Mapped[str | None] = orm.mapped_column(
        sa.String(255),
        comment="Отделение станции операции",
    )
    oper_code: orm.Mapped[str | None] = orm.mapped_column(
        sa.String(10),
        comment="Код операции",
    )
    oper_name: orm.Mapped[str | None] = orm.mapped_column(
        sa.String(100),
        comment="Операция",
    )
    oper_full_name: orm.Mapped[str | None] = orm.mapped_column(
        sa.String(512),
        comment="Полное наименование операции",
    )
    oper_date: orm.Mapped[datetime.datetime | None] = orm.mapped_column(
        sa.DateTime(timezone=True),
        comment="Дата операции",
    )

    # ── Груз ──────────────────────────────────────────────────────────────────
    cargo_weight: orm.Mapped[float | None] = orm.mapped_column(
        sa.Double,
        comment="Вес груза (кг)",
    )
    cargo_code: orm.Mapped[str | None] = orm.mapped_column(
        sa.String(20),
        comment="Код груза учётный ЕТСНГ",
    )
    cargo_name: orm.Mapped[str | None] = orm.mapped_column(
        sa.String(255),
        comment="Груз",
    )
    cargo_full_name: orm.Mapped[str | None] = orm.mapped_column(
        sa.String(512),
        comment="Полное наименование груза",
    )

    # ── Поезд ─────────────────────────────────────────────────────────────────
    train_num: orm.Mapped[str | None] = orm.mapped_column(
        sa.String(20),
        comment="Номер поезда",
    )
    train_index: orm.Mapped[str | None] = orm.mapped_column(
        sa.String(60),
        comment="Индекс поезда",
    )
    train_index_1: orm.Mapped[str | None] = orm.mapped_column(
        sa.String(20),
        comment="Индекс поезда (ст. форм.)",
    )
    train_index_2: orm.Mapped[str | None] = orm.mapped_column(
        sa.String(20),
        comment="Индекс поезда (№ н. листа)",
    )
    train_index_3: orm.Mapped[str | None] = orm.mapped_column(
        sa.String(20),
        comment="Индекс поезда (ст. назн.)",
    )
    npp: orm.Mapped[str | None] = orm.mapped_column(
        sa.String(10),
        comment="НПП",
    )
    train_from_station_name: orm.Mapped[str | None] = orm.mapped_column(
        sa.String(255),
        comment="Станция формирования поезда",
    )
    train_to_station_name: orm.Mapped[str | None] = orm.mapped_column(
        sa.String(255),
        comment="Станция расформирования поезда",
    )
    car_number: orm.Mapped[str | None] = orm.mapped_column(
        sa.String(20),
        comment="Номер платформы (для контейнеров)",
    )

    # ── Назначение ────────────────────────────────────────────────────────────
    dest_rw: orm.Mapped[str | None] = orm.mapped_column(
        sa.String(20),
        comment="Код дороги назначения",
    )
    dest_rw_name: orm.Mapped[str | None] = orm.mapped_column(
        sa.String(100),
        comment="Дорога назначения",
    )
    dest_country_name: orm.Mapped[str | None] = orm.mapped_column(
        sa.String(100),
        comment="ЖД администрация ст. назначения",
    )
    dest_station: orm.Mapped[str | None] = orm.mapped_column(
        sa.String(20),
        comment="Код станции назначения",
    )
    dest_station_name: orm.Mapped[str | None] = orm.mapped_column(
        sa.String(255),
        comment="Станция назначения",
    )
    dest_station_department: orm.Mapped[str | None] = orm.mapped_column(
        sa.String(255),
        comment="Отделение станции назначения",
    )
    delivery_date: orm.Mapped[datetime.date | None] = orm.mapped_column(
        sa.Date,
        comment="Срок доставки",
    )
    rest_distance: orm.Mapped[float | None] = orm.mapped_column(
        sa.Double,
        comment="Остаточное расстояние (км)",
    )
    rest_run: orm.Mapped[float | None] = orm.mapped_column(
        sa.Double,
        comment="Остаток пробега (км)",
    )

    # ── Получатель / Отправитель ──────────────────────────────────────────────
    grpol_okpo: orm.Mapped[str | None] = orm.mapped_column(
        sa.String(20),
        comment="ОКПО грузополучателя",
    )
    grpol_name: orm.Mapped[str | None] = orm.mapped_column(
        sa.String(255),
        comment="Наименование грузополучателя",
    )
    grpol_rw: orm.Mapped[str | None] = orm.mapped_column(
        sa.String(20),
        comment="ЖД код грузополучателя",
    )
    grotpr_okpo: orm.Mapped[str | None] = orm.mapped_column(
        sa.String(20),
        comment="ОКПО грузоотправителя",
    )
    grotpr_name: orm.Mapped[str | None] = orm.mapped_column(
        sa.String(255),
        comment="Наименование грузоотправителя",
    )
    grotpr_rw: orm.Mapped[str | None] = orm.mapped_column(
        sa.String(20),
        comment="ЖД код грузоотправителя",
    )

    # ── Источник данных ───────────────────────────────────────────────────────
    rash_rw: orm.Mapped[str | None] = orm.mapped_column(
        sa.String(20),
        comment="Код дороги — источника данных",
    )
    rash_date: orm.Mapped[datetime.datetime | None] = orm.mapped_column(
        sa.DateTime(timezone=True),
        comment="Дата обновления данных",
    )

    # ── Стоянка / счётчики ────────────────────────────────────────────────────
    start_date_on_station: orm.Mapped[datetime.datetime | None] = orm.mapped_column(
        sa.DateTime(timezone=True),
        comment="Дата прибытия на текущую станцию",
    )
    day_count_on_station: orm.Mapped[float | None] = orm.mapped_column(
        sa.Double,
        comment="Кол-во дней на станции",
    )
    days_wo_operation: orm.Mapped[float | None] = orm.mapped_column(
        sa.Double,
        comment="Дней без операции",
    )
    days_from_start: orm.Mapped[float | None] = orm.mapped_column(
        sa.Double,
        comment="Кол-во дней после погрузки",
    )
    days_on_trade_union: orm.Mapped[float | None] = orm.mapped_column(
        sa.Double,
        comment="Кол-во дней на территории ТС (Таможенный Союз)",
    )
    cl_start_at: orm.Mapped[datetime.datetime | None] = orm.mapped_column(
        sa.DateTime(timezone=True),
        comment="Дата захода на текущую страну",
    )

    # ── Неисправности ─────────────────────────────────────────────────────────
    faulty_name: orm.Mapped[str | None] = orm.mapped_column(
        sa.String(255),
        comment="Неисправность",
    )

    # ── Техпаспорт ────────────────────────────────────────────────────────────
    car_type_name: orm.Mapped[str | None] = orm.mapped_column(
        sa.String(100),
        comment="Род вагона",
    )
    date_build: orm.Mapped[datetime.date | None] = orm.mapped_column(
        sa.Date,
        comment="Дата постройки",
    )
    capacity: orm.Mapped[float | None] = orm.mapped_column(
        sa.Double,
        comment="Грузоподъёмность вагона (тонн)",
    )
    volume: orm.Mapped[float | None] = orm.mapped_column(
        sa.Double,
        comment="Объём кузова (м³)",
    )
    extended_life_time: orm.Mapped[datetime.date | None] = orm.mapped_column(
        sa.Date,
        comment="Срок службы вагона",
    )
    date_plan_repair: orm.Mapped[datetime.date | None] = orm.mapped_column(
        sa.Date,
        comment="Дата следующего ремонта",
    )

    # ── НСП ───────────────────────────────────────────────────────────────────
    nsp_indicator: orm.Mapped[str | None] = orm.mapped_column(
        sa.String(50),
        comment="Признак НСП",
    )

    # ── Сырой payload ─────────────────────────────────────────────────────────
    raw_data: orm.Mapped[dict | None] = orm.mapped_column(
        JSONB,
        comment="Сырой объект из источника на случай если понадобятся поля сверх схемы",
    )
