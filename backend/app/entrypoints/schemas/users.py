"""Request-схемы для admin user endpoints."""
from __future__ import annotations

import uuid

import pydantic

from app.shared.database.enums import UserRole


class UserCreate(pydantic.BaseModel):
    """Тело запроса для создания пользователя."""

    model_config = pydantic.ConfigDict(str_strip_whitespace=True)

    email: pydantic.EmailStr
    password: str = pydantic.Field(min_length=6, max_length=128)
    role: UserRole = UserRole.USER
    full_name: str | None = pydantic.Field(default=None, max_length=255)
    # Required для superadmin (любая компания), игнорируется для admin (своя).
    company_id: uuid.UUID | None = None


class UserUpdate(pydantic.BaseModel):
    """Тело запроса для обновления пользователя (все поля опциональны)."""

    model_config = pydantic.ConfigDict(str_strip_whitespace=True)

    email: pydantic.EmailStr | None = None
    password: str | None = pydantic.Field(default=None, min_length=6, max_length=128)
    role: UserRole | None = None
    full_name: str | None = pydantic.Field(default=None, max_length=255)
