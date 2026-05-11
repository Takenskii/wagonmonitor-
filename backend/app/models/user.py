"""User — учётная запись внутри компании."""
from __future__ import annotations

import uuid

from sqlalchemy import Enum as SAEnum
from sqlalchemy import String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.enums import UserRole
from app.models.base import Base, CompanyOwnedMixin, TimestampMixin


class User(Base, CompanyOwnedMixin, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Идентификатор пользователя",
    )
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
        comment="Email (глобально уникальный)",
        info={"group": "Профиль"},
    )
    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    role: Mapped[UserRole] = mapped_column(
        SAEnum(
            UserRole,
            name="user_role",
            native_enum=True,
            # Store actual values ("superadmin"), not member names ("SUPERADMIN")
            values_callable=lambda enum_cls: [m.value for m in enum_cls],
        ),
        nullable=False,
        default=UserRole.USER,
        comment="Роль в системе",
        info={"group": "Доступ"},
    )
    full_name: Mapped[str | None] = mapped_column(
        String(255),
        comment="ФИО",
        info={"group": "Профиль"},
    )
