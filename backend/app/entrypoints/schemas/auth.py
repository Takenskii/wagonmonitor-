"""Pydantic schemas for auth endpoints."""
from __future__ import annotations

import uuid

import pydantic

from app.shared.database.enums import UserRole


class LoginRequest(pydantic.BaseModel):
    email: pydantic.EmailStr
    password: str


class LoginResponse(pydantic.BaseModel):
    token: str
    user_id: uuid.UUID
    email: pydantic.EmailStr
    full_name: str | None
    role: UserRole
    company_id: uuid.UUID
    company_name: str


class MeResponse(pydantic.BaseModel):
    id: uuid.UUID
    email: pydantic.EmailStr
    full_name: str | None
    role: UserRole
    company_id: uuid.UUID
    company_name: str
