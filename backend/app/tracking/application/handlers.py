"""Write-слой для tracking-домена: assign / remove / move."""
from __future__ import annotations

import datetime
import uuid

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from app.entrypoints.dependencies import Identity
from app.groups.domain.models import WagonGroup
from app.tracking.domain.models import TrackingAssignment


class ConflictError(Exception):
    """Конфликт в параметрах (например указаны и group_id и new_group_name)."""


async def assign_wagons(
    *,
    wagon_numbers: list[str],
    actor: Identity,
    session: AsyncSession,
    group_id: uuid.UUID | None = None,
    new_group_name: str | None = None,
    initial_territory: str | None = None,
    remove_on_route_end: bool = False,
    deferred_start_at: datetime.datetime | None = None,
    auto_remove_at: datetime.datetime | None = None,
) -> dict:
    """
    Поставить вагон(ы) на слежение у компании текущего actor'а.

    Семантика:
      - Если вагона ещё нет в tracking_assignments этой компании → создать запись.
      - Если есть и неактивен → реактивировать (active=true, removed_at=null).
      - Если есть и активен → обновить параметры (группа, тариф-территория, авто-снятие).

    Если задан `new_group_name` — создать новую группу (или взять существующую
    с таким именем в этой компании) и закинуть туда вагоны.

    Returns: {"assigned": [...], "group_id": uuid | None}
    """
    if group_id is not None and new_group_name:
        raise ConflictError("Specify either group_id or new_group_name, not both")

    # Resolve target group
    target_group_id: uuid.UUID | None = None
    if new_group_name:
        existing_group_stmt = sa.select(WagonGroup).where(
            WagonGroup.company_id == actor.company_id,
            WagonGroup.name == new_group_name,
        )
        group = await session.scalar(existing_group_stmt)
        if group is None:
            group = WagonGroup(company_id=actor.company_id, name=new_group_name)
            session.add(group)
            await session.flush()  # populate group.id
        target_group_id = group.id
    elif group_id is not None:
        group = await session.scalar(
            sa.select(WagonGroup).where(
                WagonGroup.id == group_id,
                WagonGroup.company_id == actor.company_id,
            )
        )
        if group is None:
            raise LookupError(f"Group {group_id} not found in this company")
        target_group_id = group.id

    assigned: list[str] = []
    for number in wagon_numbers:
        if not number.strip():
            continue
        number = number.strip()

        existing = await session.scalar(
            sa.select(TrackingAssignment).where(
                TrackingAssignment.company_id == actor.company_id,
                TrackingAssignment.wagon_number == number,
            )
        )
        if existing is not None:
            existing.active = True
            existing.removed_at = None
            existing.group_id = target_group_id
            existing.initial_territory = initial_territory or existing.initial_territory
            existing.remove_on_route_end = remove_on_route_end
            existing.deferred_start_at = deferred_start_at
            existing.auto_remove_at = auto_remove_at
        else:
            session.add(
                TrackingAssignment(
                    company_id=actor.company_id,
                    wagon_number=number,
                    group_id=target_group_id,
                    active=True,
                    initial_territory=initial_territory,
                    remove_on_route_end=remove_on_route_end,
                    deferred_start_at=deferred_start_at,
                    auto_remove_at=auto_remove_at,
                )
            )
        assigned.append(number)

    await session.commit()
    return {"assigned": assigned, "group_id": target_group_id}


async def remove_wagons(
    *,
    wagon_numbers: list[str],
    actor: Identity,
    session: AsyncSession,
) -> dict:
    """
    Снять вагон(ы) со слежения. Soft-delete: active=false, removed_at=now.

    Если вагон уже неактивен (или его нет в слежении) — попадает в `not_found`.
    """
    now = datetime.datetime.now(tz=datetime.UTC)
    removed: list[str] = []
    not_found: list[str] = []

    for number in wagon_numbers:
        if not number.strip():
            continue
        number = number.strip()

        ta = await session.scalar(
            sa.select(TrackingAssignment).where(
                TrackingAssignment.company_id == actor.company_id,
                TrackingAssignment.wagon_number == number,
                TrackingAssignment.active.is_(True),
            )
        )
        if ta is None:
            not_found.append(number)
            continue

        ta.active = False
        ta.removed_at = now
        removed.append(number)

    await session.commit()
    return {"removed": removed, "not_found": not_found}


async def move_wagons(
    *,
    wagon_numbers: list[str],
    actor: Identity,
    session: AsyncSession,
    group_id: uuid.UUID | None = None,
    new_group_name: str | None = None,
) -> dict:
    """
    Переложить вагоны в другую группу (или вынуть из групп если group_id=None).

    Только для активных вагонов под слежением у текущей компании.
    """
    if group_id is not None and new_group_name:
        raise ConflictError("Specify either group_id or new_group_name, not both")

    target_group_id: uuid.UUID | None = None
    if new_group_name:
        existing = await session.scalar(
            sa.select(WagonGroup).where(
                WagonGroup.company_id == actor.company_id,
                WagonGroup.name == new_group_name,
            )
        )
        if existing is None:
            existing = WagonGroup(company_id=actor.company_id, name=new_group_name)
            session.add(existing)
            await session.flush()
        target_group_id = existing.id
    elif group_id is not None:
        group = await session.scalar(
            sa.select(WagonGroup).where(
                WagonGroup.id == group_id,
                WagonGroup.company_id == actor.company_id,
            )
        )
        if group is None:
            raise LookupError(f"Group {group_id} not found in this company")
        target_group_id = group.id

    moved: list[str] = []
    for number in wagon_numbers:
        if not number.strip():
            continue
        number = number.strip()
        ta = await session.scalar(
            sa.select(TrackingAssignment).where(
                TrackingAssignment.company_id == actor.company_id,
                TrackingAssignment.wagon_number == number,
                TrackingAssignment.active.is_(True),
            )
        )
        if ta is None:
            continue
        ta.group_id = target_group_id
        moved.append(number)

    await session.commit()
    return {"moved": moved, "group_id": target_group_id}
