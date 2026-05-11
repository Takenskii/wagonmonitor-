"""Company — корпоративный клиент платформы."""
from __future__ import annotations

import uuid

from sqlalchemy import String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class Company(Base, TimestampMixin):
    __tablename__ = "companies"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Идентификатор компании",
    )
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Название компании",
        info={"group": "Реквизиты"},
    )
    # Остальные реквизиты, банковские данные, billing_rates — добавятся при
    # портировании соответствующих модулей (документы, биллинг).
