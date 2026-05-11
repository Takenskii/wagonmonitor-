"""Pydantic schemas for User admin endpoints."""
from __future__ import annotations

import datetime
import uuid

import pydantic

from app.shared.database.enums import UserRole


class UserCreate(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(str_strip_whitespace=True)

    email: pydantic.EmailStr
    password: str = pydantic.Field(min_length=6, max_length=128)
    role: UserRole = UserRole.USER
    full_name: str | None = pydantic.Field(default=None, max_length=255)
    # Required for superadmin (any company), ignored for company_admin (uses own).
    company_id: uuid.UUID | None = None


class UserUpdate(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(str_strip_whitespace=True)

    email: pydantic.EmailStr | None = None
    password: str | None = pydantic.Field(default=None, min_length=6, max_length=128)
    role: UserRole | None = None
    full_name: str | None = pydantic.Field(default=None, max_length=255)


class UserOut(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: pydantic.EmailStr
    full_name: str | None
    role: UserRole
    company_id: uuid.UUID
    created_at: datetime.datetime
    updated_at: datetime.datetime
