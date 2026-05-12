"""TrackingAssignment — какие вагоны под слежением у какой компании.

`wagon_number` — VARCHAR без FK на `wagons.id` (намеренно):
ingestion может получить вагон, у которого уже есть assignment у компании,
или наоборот — assignment создан раньше первого появления вагона в данных.
Связь через бизнес-идентификатор.

UNIQUE (company_id, wagon_number) — один и тот же вагон не может быть в
слежении дважды у одной компании.
"""
from __future__ import annotations

import datetime
import uuid

import sqlalchemy as sa
from sqlalchemy import orm

from app.shared.database.base import Base


class TrackingAssignment(Base):
    __tablename__ = "tracking_assignments"
    __table_args__ = (
        sa.UniqueConstraint(
            "company_id", "wagon_number",
            name="uq_tracking_company_wagon",
        ),
    )

    company_id: orm.Mapped[uuid.UUID] = orm.mapped_column(
        sa.ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Компания, которая следит",
    )
    wagon_number: orm.Mapped[str] = orm.mapped_column(
        sa.String(20),
        nullable=False,
        index=True,
        comment="Номер вагона (бизнес-идентификатор)",
    )
    group_id: orm.Mapped[uuid.UUID | None] = orm.mapped_column(
        sa.ForeignKey("wagon_groups.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="Группа в которой вагон у этой компании",
    )

    # Soft-delete + временные правила
    active: orm.Mapped[bool] = orm.mapped_column(
        sa.Boolean,
        nullable=False,
        default=True,
        server_default=sa.text("true"),
        comment="Активно ли слежение",
    )
    removed_at: orm.Mapped[datetime.datetime | None] = orm.mapped_column(
        sa.DateTime(timezone=True),
        comment="Когда слежение было снято",
    )
    initial_territory: orm.Mapped[str | None] = orm.mapped_column(
        sa.String(100),
        comment="Страна на момент постановки (для биллинга)",
    )
    remove_on_route_end: orm.Mapped[bool] = orm.mapped_column(
        sa.Boolean,
        nullable=False,
        default=False,
        server_default=sa.text("false"),
        comment="Автоматически снять когда вагон достигнет dest_station",
    )
    deferred_start_at: orm.Mapped[datetime.datetime | None] = orm.mapped_column(
        sa.DateTime(timezone=True),
        comment="Отложенный старт слежения (активируется не сразу)",
    )
    auto_remove_at: orm.Mapped[datetime.datetime | None] = orm.mapped_column(
        sa.DateTime(timezone=True),
        comment="Автоматически снять в указанную дату",
    )
