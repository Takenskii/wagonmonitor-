"""Company — корпоративный клиент платформы."""
from __future__ import annotations

from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy import orm

from app.shared.database.base import Base

if TYPE_CHECKING:
    from app.users.domain.models import User


class Company(Base):
    __tablename__ = "companies"

    name: orm.Mapped[str] = orm.mapped_column(
        sa.String(255),
        nullable=False,
        comment="Название компании",
        info={"group": "Реквизиты"},
    )

    users: orm.Mapped[list[User]] = orm.relationship(
        back_populates="company",
        cascade="all, delete-orphan",
    )
