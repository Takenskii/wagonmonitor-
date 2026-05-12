"""Request-схемы для admin company endpoints."""
from __future__ import annotations

import pydantic


class CompanyCreate(pydantic.BaseModel):
    """Тело запроса для создания компании."""

    model_config = pydantic.ConfigDict(str_strip_whitespace=True)

    name: str = pydantic.Field(min_length=1, max_length=255)


class CompanyUpdate(pydantic.BaseModel):
    """Тело запроса для обновления компании (все поля опциональны)."""

    model_config = pydantic.ConfigDict(str_strip_whitespace=True)

    name: str | None = pydantic.Field(default=None, min_length=1, max_length=255)
