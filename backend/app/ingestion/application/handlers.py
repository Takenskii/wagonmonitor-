"""Бизнес-логика ingestion'а: upsert вагонов через PostgreSQL ON CONFLICT."""
from __future__ import annotations

import datetime
import logging
import uuid
from typing import Any

from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.wagons.domain.models import Wagon

log = logging.getLogger(__name__)

# Колонки которыми Base/ORM управляет автоматически — их не трогаем из payload'а
_AUTO_MANAGED = {"pk", "id", "created_at", "updated_at", "first_seen", "raw_data"}
_WAGON_COLUMNS = {c.name for c in Wagon.__table__.columns} - _AUTO_MANAGED


async def ingest_batch(
    items: list[dict[str, Any]],
    *,
    source: str,
    db: AsyncSession,
) -> dict[str, int]:
    """
    Upsert вагонов по `wagon_number`.

    Каждый item — dict с полями вагона. Уже отвалидирован через
    Pydantic-схему `WagonIngestItem` на entrypoint-уровне.

    Возвращает счётчики: общее, успешно обновлено, ошибок.
    """
    now = datetime.datetime.now(tz=datetime.UTC)
    updated = 0
    errors = 0

    for item in items:
        number = item.get("number")
        if not number:
            errors += 1
            continue

        try:
            # Фильтруем поля до тех, что есть в таблице Wagon
            data = {k: v for k, v in item.items() if k in _WAGON_COLUMNS}
            data["number"] = number
            data["last_seen"] = now
            data["last_source"] = source

            # Полный INSERT: добавляем поля которые Python-default'ом ORM поставил бы,
            # но pg_insert их не вызывает (raw SQL).
            insert_values = {
                **data,
                "id": uuid.uuid4(),
                "first_seen": now,
                "created_at": now,
                "updated_at": now,
                "raw_data": item,  # сохраняем оригинал payload'а
            }

            # При UPDATE on conflict — не трогаем first_seen, created_at, id, number
            update_values = {
                **data,
                "updated_at": now,
                "raw_data": item,
            }
            update_values.pop("number", None)

            stmt = (
                pg_insert(Wagon)
                .values(**insert_values)
                .on_conflict_do_update(
                    index_elements=["number"],
                    set_=update_values,
                )
            )
            await db.execute(stmt)
            updated += 1
        except Exception:
            log.exception("Не удалось обновить вагон %r", number)
            errors += 1

    await db.commit()
    return {
        "wagons_total": len(items),
        "wagons_updated": updated,
        "errors": errors,
    }
