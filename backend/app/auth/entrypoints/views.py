"""Authentication endpoints: login + me."""
from __future__ import annotations

import fastapi

from app.auth.application import handlers, views
from app.auth.application.handlers import InvalidCredentialsError
from app.entrypoints.dependencies import CurrentUser, Session
from app.entrypoints.schemas.auth import LoginRequest, LoginResponse, MeResponse

router = fastapi.APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post(
    "/login/",
    summary="Вход в систему",
    response_model=LoginResponse,
    status_code=fastapi.status.HTTP_200_OK,
    responses={
        200: {"description": "Успешная авторизация — возвращается JWT"},
        401: {"description": "Неверный email или пароль"},
    },
)
async def login(req: LoginRequest, db: Session) -> LoginResponse:
    """
    Аутентификация пользователя.

    Принимает email + пароль, проверяет учётные данные, возвращает JWT-токен.
    """
    try:
        token, user_view = await handlers.login(
            email=req.email, password=req.password, session=db,
        )
    except InvalidCredentialsError:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        ) from None

    return LoginResponse(
        token=token,
        user_id=user_view.id,
        email=user_view.email,
        full_name=user_view.full_name,
        role=user_view.role,
        company_id=user_view.company_id,
        company_name=user_view.company_name,
    )


@router.get(
    "/me/",
    summary="Текущий пользователь",
    response_model=MeResponse,
    status_code=fastapi.status.HTTP_200_OK,
    responses={
        200: {"description": "Данные текущего пользователя"},
        401: {"description": "Не аутентифицирован"},
        404: {"description": "Пользователь не найден"},
    },
)
async def me(current: CurrentUser, db: Session) -> MeResponse:
    """
    Получение данных текущего пользователя по JWT-токену.
    """
    try:
        user_view = await views.get_me_view(user_id=current.user_id, session=db)
    except LookupError:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_404_NOT_FOUND, detail="User not found"
        ) from None

    return MeResponse(
        id=user_view.id,
        email=user_view.email,
        full_name=user_view.full_name,
        role=user_view.role,
        company_id=user_view.company_id,
        company_name=user_view.company_name,
    )
