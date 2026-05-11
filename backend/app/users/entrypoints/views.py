"""Admin endpoints for User management.

Scope:
  - superadmin: any user in any company (optional ?company_id= filter)
  - admin:      users in own company only
"""
from __future__ import annotations

import uuid
from typing import Annotated

import fastapi
import sqlalchemy as sa
from sqlalchemy.ext import asyncio as asa

from app.companies.domain.models import Company
from app.entrypoints.dependencies import CompanyAdmin, Identity, Session
from app.entrypoints.schemas.users import UserCreate, UserOut, UserUpdate
from app.shared.database.enums import UserRole
from app.shared.security import hash_password
from app.users.domain.models import User

router = fastapi.APIRouter(
    prefix="/api/v1/admin/users",
    tags=["admin:users"],
)


def _can_access(actor: Identity, target_company_id: uuid.UUID) -> bool:
    if actor.role == UserRole.SUPERADMIN:
        return True
    return actor.company_id == target_company_id


async def _get_or_404(db: asa.AsyncSession, user_id: uuid.UUID) -> User:
    result = await db.execute(sa.select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise fastapi.HTTPException(status_code=404, detail="User not found")
    return user


async def _resolve_company_pk(db: asa.AsyncSession, company_id: uuid.UUID) -> int:
    """Map external UUID id to internal int pk (FK column on users is company_id UUID)."""
    result = await db.execute(sa.select(Company.id).where(Company.id == company_id))
    found = result.scalar_one_or_none()
    if found is None:
        raise fastapi.HTTPException(status_code=400, detail="Company not found")
    return found  # type: ignore[return-value]


@router.post("", response_model=UserOut, status_code=201)
async def create_user(req: UserCreate, actor: CompanyAdmin, db: Session) -> User:
    # Resolve target company by actor role
    if actor.role == UserRole.SUPERADMIN:
        if req.company_id is None:
            raise fastapi.HTTPException(
                status_code=400, detail="company_id is required for superadmin"
            )
        target_company_id = req.company_id
    else:
        # admin always operates within own company; req.company_id ignored
        target_company_id = actor.company_id

    # Sanity-check company exists
    company_exists = await db.execute(
        sa.select(Company.id).where(Company.id == target_company_id)
    )
    if company_exists.scalar_one_or_none() is None:
        raise fastapi.HTTPException(status_code=404, detail="Company not found")

    # Only superadmin can grant superadmin role
    if req.role == UserRole.SUPERADMIN and actor.role != UserRole.SUPERADMIN:
        raise fastapi.HTTPException(
            status_code=403, detail="Only superadmin can grant superadmin role"
        )

    user = User(
        email=req.email,
        password_hash=await hash_password(req.password),
        role=req.role,
        full_name=req.full_name,
        company_id=target_company_id,
    )
    db.add(user)
    try:
        await db.commit()
    except sa.exc.IntegrityError as e:
        await db.rollback()
        raise fastapi.HTTPException(status_code=409, detail="Email already exists") from e
    await db.refresh(user)
    return user


@router.get("", response_model=list[UserOut])
async def list_users(
    actor: CompanyAdmin,
    db: Session,
    company_id: Annotated[uuid.UUID | None, fastapi.Query()] = None,
) -> list[User]:
    stmt = sa.select(User).order_by(User.created_at.desc())
    if actor.role == UserRole.SUPERADMIN:
        if company_id is not None:
            stmt = stmt.where(User.company_id == company_id)
    else:
        stmt = stmt.where(User.company_id == actor.company_id)
    result = await db.execute(stmt)
    return list(result.scalars().all())


@router.get("/{user_id}", response_model=UserOut)
async def get_user(user_id: uuid.UUID, actor: CompanyAdmin, db: Session) -> User:
    user = await _get_or_404(db, user_id)
    if not _can_access(actor, user.company_id):
        raise fastapi.HTTPException(status_code=404, detail="User not found")
    return user


@router.patch("/{user_id}", response_model=UserOut)
async def update_user(
    user_id: uuid.UUID,
    req: UserUpdate,
    actor: CompanyAdmin,
    db: Session,
) -> User:
    user = await _get_or_404(db, user_id)
    if not _can_access(actor, user.company_id):
        raise fastapi.HTTPException(status_code=404, detail="User not found")

    if req.email is not None:
        user.email = req.email
    if req.full_name is not None:
        user.full_name = req.full_name
    if req.role is not None:
        # Only superadmin can grant superadmin or change role to superadmin
        if req.role == UserRole.SUPERADMIN and actor.role != UserRole.SUPERADMIN:
            raise fastapi.HTTPException(
                status_code=403, detail="Only superadmin can grant superadmin role"
            )
        user.role = req.role
    if req.password is not None:
        user.password_hash = await hash_password(req.password)

    try:
        await db.commit()
    except sa.exc.IntegrityError as e:
        await db.rollback()
        raise fastapi.HTTPException(status_code=409, detail="Email already exists") from e
    await db.refresh(user)
    return user


@router.delete("/{user_id}", status_code=204)
async def delete_user(user_id: uuid.UUID, actor: CompanyAdmin, db: Session) -> None:
    user = await _get_or_404(db, user_id)
    if not _can_access(actor, user.company_id):
        raise fastapi.HTTPException(status_code=404, detail="User not found")
    if user.id == actor.user_id:
        raise fastapi.HTTPException(status_code=400, detail="Cannot delete yourself")
    await db.delete(user)
    await db.commit()
