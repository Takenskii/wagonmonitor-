"""Authentication endpoints: login + me."""
from __future__ import annotations

import fastapi
import sqlalchemy as sa

from app.companies.domain.models import Company
from app.entrypoints.dependencies import CurrentUser, Session
from app.entrypoints.schemas.auth import LoginRequest, LoginResponse, MeResponse
from app.shared.security import create_access_token, verify_password
from app.users.domain.models import User

router = fastapi.APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
async def login(req: LoginRequest, db: Session) -> LoginResponse:
    result = await db.execute(
        sa.select(User, Company)
        .join(Company, Company.id == User.company_id)
        .where(User.email == req.email)
    )
    row = result.first()
    if row is None:
        raise fastapi.HTTPException(status_code=401, detail="Invalid credentials")
    user, company = row
    if not await verify_password(req.password, user.password_hash):
        raise fastapi.HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(
        user_id=user.id,
        company_id=company.id,
        role=user.role.value,
    )
    return LoginResponse(
        token=token,
        user_id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        company_id=company.id,
        company_name=company.name,
    )


@router.get("/me", response_model=MeResponse)
async def me(current: CurrentUser, db: Session) -> MeResponse:
    result = await db.execute(
        sa.select(User, Company)
        .join(Company, Company.id == User.company_id)
        .where(User.id == current.user_id)
    )
    row = result.first()
    if row is None:
        raise fastapi.HTTPException(status_code=404, detail="User not found")
    user, company = row
    return MeResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        company_id=company.id,
        company_name=company.name,
    )
