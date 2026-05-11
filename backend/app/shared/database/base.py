"""ORM base class."""
from __future__ import annotations

import datetime
import functools
import uuid

import sqlalchemy as sa
from sqlalchemy import orm

datetime_now_tz = functools.partial(datetime.datetime.now, tz=datetime.UTC)


class Base(orm.DeclarativeBase):
    """
    Declarative base — every model gets:
      - `pk`: int primary key (internal, ordering)
      - `id`: UUID, used by foreign keys and external API references
      - `created_at`, `updated_at`: timezone-aware Python-side timestamps
    """

    pk: orm.Mapped[int] = orm.mapped_column(primary_key=True)
    id: orm.Mapped[uuid.UUID] = orm.mapped_column(unique=True, default=uuid.uuid4)
    created_at: orm.Mapped[datetime.datetime] = orm.mapped_column(
        sa.DateTime(timezone=True),
        default=datetime_now_tz,
    )
    updated_at: orm.Mapped[datetime.datetime] = orm.mapped_column(
        sa.DateTime(timezone=True),
        default=datetime_now_tz,
        onupdate=datetime_now_tz,
    )
