"""FastAPI dependencies — auth + DB session + type aliases for routers."""
from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Annotated

import fastapi
import fastapi.security
from jwt.exceptions import InvalidTokenError
from sqlalchemy.ext import asyncio as asa

from app.shared.database.enums import UserRole
from app.shared.database.session import get_session
from app.shared.security import decode_token

oauth2_scheme = fastapi.security.HTTPBearer(auto_error=False)


@dataclass(frozen=True, slots=True)
class Identity:
    """Claims extracted from a valid JWT. No DB round-trip — pure decode."""

    user_id: uuid.UUID
    company_id: uuid.UUID
    role: UserRole
    # Set when a superadmin is impersonating this user — for audit trail.
    impersonated_by: uuid.UUID | None = None


async def get_current_user(
    auth: Annotated[
        fastapi.security.HTTPAuthorizationCredentials | None,
        fastapi.Depends(oauth2_scheme),
    ],
) -> Identity:
    if auth is None or not auth.credentials:
        raise fastapi.HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = decode_token(auth.credentials)
        impersonated_by_raw = payload.get("impersonated_by")
        return Identity(
            user_id=uuid.UUID(payload["user_id"]),
            company_id=uuid.UUID(payload["company_id"]),
            role=UserRole(payload["role"]),
            impersonated_by=uuid.UUID(impersonated_by_raw) if impersonated_by_raw else None,
        )
    except (InvalidTokenError, KeyError, ValueError) as e:
        raise fastapi.HTTPException(
            status_code=401, detail="Invalid or expired token"
        ) from e


async def require_superadmin(
    identity: Annotated[Identity, fastapi.Depends(get_current_user)],
) -> Identity:
    if identity.role != UserRole.SUPERADMIN:
        raise fastapi.HTTPException(status_code=403, detail="Superadmin only")
    return identity


async def require_company_admin(
    identity: Annotated[Identity, fastapi.Depends(get_current_user)],
) -> Identity:
    """ADMIN of a company OR SUPERADMIN of the platform."""
    if identity.role not in (UserRole.SUPERADMIN, UserRole.ADMIN):
        raise fastapi.HTTPException(status_code=403, detail="Admin only")
    return identity


# ── Type aliases used in router signatures ────────────────────────────────────
# Usage:
#   async def me(current: CurrentUser, db: Session) -> MeResponse: ...
Session = Annotated[asa.AsyncSession, fastapi.Depends(get_session)]
CurrentUser = Annotated[Identity, fastapi.Depends(get_current_user)]
Superadmin = Annotated[Identity, fastapi.Depends(require_superadmin)]
CompanyAdmin = Annotated[Identity, fastapi.Depends(require_company_admin)]
