"""User — учётная запись внутри компании."""
from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy import orm

from app.shared.database.base import Base
from app.shared.database.enums import UserRole

if TYPE_CHECKING:
    from app.companies.domain.models import Company


class User(Base):
    __tablename__ = "users"

    email: orm.Mapped[str] = orm.mapped_column(
        sa.String(255),
        unique=True,
        nullable=False,
        index=True,
        comment="Email (глобально уникальный)",
        info={"group": "Профиль"},
    )
    password_hash: orm.Mapped[str] = orm.mapped_column(
        sa.String(255),
        nullable=False,
    )
    role: orm.Mapped[UserRole] = orm.mapped_column(
        sa.Enum(
            UserRole,
            name="user_role",
            native_enum=True,
            values_callable=lambda enum_cls: [m.value for m in enum_cls],
        ),
        nullable=False,
        default=UserRole.USER,
        comment="Роль в системе",
        info={"group": "Доступ"},
    )
    full_name: orm.Mapped[str | None] = orm.mapped_column(
        sa.String(255),
        comment="ФИО",
        info={"group": "Профиль"},
    )

    company_id: orm.Mapped[uuid.UUID] = orm.mapped_column(
        sa.ForeignKey("companies.id", ondelete="CASCADE"),
        index=True,
    )
    company: orm.Mapped[Company] = orm.relationship(back_populates="users")
