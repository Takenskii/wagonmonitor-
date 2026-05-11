"""ORM base class + shared mixins."""
from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Declarative base for all ORM models."""


class TimestampMixin:
    """Adds `created_at` with server-side default."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )


class CompanyOwnedMixin:
    """
    Adds `company_id` FK to `companies.id` (CASCADE on delete) + index.

    Any model representing company-scoped data must inherit from this.
    Queries against such models go through `deps.company_query()` helper —
    never bare `select(Model).where(Model.company_id == ...)` in routers.
    """

    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
