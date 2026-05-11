"""Application settings. Single source of truth for env-driven config."""
import pathlib
from typing import Annotated, Literal

import pydantic
import pydantic_settings as pds

# backend/app/config.py → repo root (.env lives there)
_REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent.parent


class DatabaseSettings(pydantic.BaseModel):
    host: str
    port: int = 5432
    user: str
    password: str
    name: str
    pool_size: int = 10
    max_overflow: int = 20
    echo: bool = False

    @property
    def dsn(self) -> str:
        return (
            f"postgresql+asyncpg://"
            f"{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"
        )


class JWTSettings(pydantic.BaseModel):
    secret: str
    algorithm: str = "HS256"
    expire_hours: int = 24
    reset_expire_hours: int = 2

    @pydantic.field_validator("secret")
    @classmethod
    def _strong_enough(cls, v: str) -> str:
        if len(v) < 32:
            raise ValueError(
                "jwt.secret must be at least 32 chars. "
                "Generate: python -c 'import secrets; print(secrets.token_urlsafe(48))'"
            )
        return v


class SMTPSettings(pydantic.BaseModel):
    host: str = ""
    port: int = 587
    user: str = ""
    password: str = ""
    use_tls: bool = False
    start_tls: bool = True
    timeout: int = 30
    from_addr: str = ""


class Settings(pds.BaseSettings):
    """Application settings."""

    model_config = pds.SettingsConfigDict(
        extra="ignore",
        env_file=_REPO_ROOT / ".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
    )

    database: DatabaseSettings
    jwt: JWTSettings
    smtp: SMTPSettings = SMTPSettings()

    # Annotated[..., NoDecode] tells pydantic-settings to skip JSON-decoding,
    # so our `_parse_csv` validator can split the comma-separated string.
    cors_origins: Annotated[set[str], pds.NoDecode] = set()
    public_url: pydantic.HttpUrl = pydantic.HttpUrl("http://localhost")
    app_timezone: str = "Asia/Almaty"
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"

    default_page_size: int = 25
    max_page_size: int = 1000
    max_ingest_batch: int = 10_000

    is_test: bool = False

    @pydantic.field_validator("cors_origins", mode="before")
    @classmethod
    def _parse_csv(cls, v: object) -> object:
        """Accept comma-separated string from env, fall through for list/set inputs."""
        if isinstance(v, str):
            return {o.strip() for o in v.split(",") if o.strip()}
        return v

    @pydantic.field_validator("cors_origins")
    @classmethod
    def _no_wildcard(cls, v: set[str]) -> set[str]:
        if "*" in v:
            raise ValueError("cors_origins must not contain '*' — list explicit origins")
        return v


settings = Settings()  # type: ignore[call-arg]
