"""Request-схемы для tracking endpoints."""
from __future__ import annotations

import datetime
import uuid

import pydantic


class AssignRequest(pydantic.BaseModel):
    """Тело запроса для POST /tracking/assign/."""

    model_config = pydantic.ConfigDict(str_strip_whitespace=True)

    wagon_numbers: list[str] = pydantic.Field(
        min_length=1, max_length=1000,
        description="Номера вагонов/контейнеров для постановки на слежение",
    )
    group_id: uuid.UUID | None = pydantic.Field(
        default=None,
        description="ID существующей группы (взаимоисключающе с new_group_name)",
    )
    new_group_name: str | None = pydantic.Field(
        default=None, max_length=255,
        description="Название новой группы — создастся и в неё попадут вагоны",
    )
    initial_territory: str | None = pydantic.Field(
        default=None, max_length=100,
        description="Страна на момент постановки (для биллинга)",
    )
    remove_on_route_end: bool = pydantic.Field(
        default=False,
        description="Автоматически снять слежение когда вагон доедет до станции назначения",
    )
    deferred_start_at: datetime.datetime | None = pydantic.Field(
        default=None,
        description="Отложенный старт — слежение активируется не сразу",
    )
    auto_remove_at: datetime.datetime | None = pydantic.Field(
        default=None,
        description="Автоматически снять в указанную дату",
    )


class AssignResponse(pydantic.BaseModel):
    """Ответ POST /tracking/assign/."""

    assigned: list[str] = pydantic.Field(
        description="Номера вагонов, успешно поставленные на слежение или реактивированные",
    )
    group_id: uuid.UUID | None = pydantic.Field(
        default=None,
        description="ID группы в которую попали вагоны (если задана)",
    )


class RemoveRequest(pydantic.BaseModel):
    """Тело запроса для POST /tracking/remove/ — снятие со слежения."""

    model_config = pydantic.ConfigDict(str_strip_whitespace=True)

    wagon_numbers: list[str] = pydantic.Field(
        min_length=1, max_length=1000,
        description="Номера вагонов которые снять со слежения",
    )


class RemoveResponse(pydantic.BaseModel):
    removed: list[str] = pydantic.Field(
        description="Номера вагонов, действительно снятых (которые были активны)",
    )
    not_found: list[str] = pydantic.Field(
        default_factory=list,
        description="Номера вагонов, которые не были под слежением (пропущены)",
    )


class MoveRequest(pydantic.BaseModel):
    """Тело запроса для POST /tracking/move/ — переместить вагоны в другую группу."""

    model_config = pydantic.ConfigDict(str_strip_whitespace=True)

    wagon_numbers: list[str] = pydantic.Field(
        min_length=1, max_length=1000,
        description="Номера вагонов которые перемещаются",
    )
    group_id: uuid.UUID | None = pydantic.Field(
        default=None,
        description="ID целевой группы (null = вынуть из всех групп, в 'Вне группы')",
    )
    new_group_name: str | None = pydantic.Field(
        default=None, max_length=255,
        description="Создать новую группу с этим именем и переложить туда",
    )


class MoveResponse(pydantic.BaseModel):
    moved: list[str] = pydantic.Field(description="Номера вагонов, перемещённых в новую группу")
    group_id: uuid.UUID | None = pydantic.Field(default=None)
