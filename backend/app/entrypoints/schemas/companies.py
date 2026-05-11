"""Pydantic schemas for Company admin endpoints."""
from __future__ import annotations

import datetime
import uuid

import pydantic


class CompanyCreate(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(str_strip_whitespace=True)

    name: str = pydantic.Field(min_length=1, max_length=255)


class CompanyUpdate(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(str_strip_whitespace=True)

    name: str | None = pydantic.Field(default=None, min_length=1, max_length=255)


class CompanyOut(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    created_at: datetime.datetime
    updated_at: datetime.datetime
