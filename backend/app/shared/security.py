"""Password hashing + JWT issuance/verification."""
from __future__ import annotations

import asyncio
import datetime
import functools
import uuid

import bcrypt
import jwt

from app.shared.contrib.config import settings

datetime_now_tz = functools.partial(datetime.datetime.now, tz=datetime.UTC)


async def hash_password(plain: str) -> str:
    """bcrypt is CPU-bound (~250ms at default rounds) — run off the event loop."""
    return await asyncio.to_thread(
        lambda: bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()
    )


async def verify_password(plain: str, hashed: str) -> bool:
    return await asyncio.to_thread(
        lambda: bcrypt.checkpw(plain.encode(), hashed.encode())
    )


def create_access_token(
    *,
    user_id: uuid.UUID,
    company_id: uuid.UUID,
    role: str,
    impersonated_by: uuid.UUID | None = None,
) -> str:
    now = datetime_now_tz()
    payload: dict[str, object] = {
        "user_id": str(user_id),
        "company_id": str(company_id),
        "role": role,
        "iat": now,
        "exp": now + datetime.timedelta(hours=settings.jwt.expire_hours),
    }
    if impersonated_by is not None:
        payload["impersonated_by"] = str(impersonated_by)
    return jwt.encode(payload, settings.jwt.secret, algorithm=settings.jwt.algorithm)


def decode_token(token: str) -> dict:
    return jwt.decode(token, settings.jwt.secret, algorithms=[settings.jwt.algorithm])
