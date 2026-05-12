"""WagonGroup — компании группируют свои вагоны на слежении."""
from __future__ import annotations

import uuid

import sqlalchemy as sa
from sqlalchemy import orm

from app.shared.database.base import Base


class WagonGroup(Base):
    __tablename__ = "wagon_groups"
    __table_args__ = (
        # Имя группы уникально в рамках компании
        sa.UniqueConstraint("company_id", "name", name="uq_wagon_groups_company_name"),
    )

    company_id: orm.Mapped[uuid.UUID] = orm.mapped_column(
        sa.ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Компания-владелец группы",
    )
    name: orm.Mapped[str] = orm.mapped_column(
        sa.String(255),
        nullable=False,
        comment="Название группы",
    )
    color: orm.Mapped[str | None] = orm.mapped_column(
        sa.String(7),
        comment="HEX-цвет для UI (#RRGGBB)",
    )
