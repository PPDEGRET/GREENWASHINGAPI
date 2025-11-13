"""Centralised application settings loaded from environment variables."""
from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache


def _load_dotenv() -> None:
    """Best-effort loading of a local .env file."""

    try:
        from dotenv import load_dotenv
    except Exception:  # pragma: no cover - fallback if optional dep missing
        load_dotenv = None

    if callable(load_dotenv):
        load_dotenv()


class MissingEnvironmentVariable(RuntimeError):
    """Raised when a required environment variable is absent or empty."""

    def __init__(self, name: str) -> None:
        super().__init__(f"Missing required environment variable: {name}")
        self.name = name


@dataclass(frozen=True)
class Settings:
    """Container for environment driven configuration."""

    supabase_url: str
    supabase_anon_key: str
    supabase_service_role: str | None
    app_base_url: str
    openai_api_key: str | None

    def require_service_role(self) -> str:
        """Return the Supabase service role key or raise if missing."""

        if not self.supabase_service_role:
            raise MissingEnvironmentVariable("SUPABASE_SERVICE_ROLE")
        return self.supabase_service_role


def _get_required_env(name: str) -> str:
    value = os.getenv(name)
    if not value or not value.strip():
        raise MissingEnvironmentVariable(name)
    return value.strip()


def _get_optional_env(name: str, default: str | None = None) -> str | None:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip() or default


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Load application settings from the environment (cached)."""

    _load_dotenv()
    return Settings(
        supabase_url=_get_required_env("SUPABASE_URL"),
        supabase_anon_key=_get_required_env("SUPABASE_ANON_KEY"),
        supabase_service_role=_get_optional_env("SUPABASE_SERVICE_ROLE"),
        app_base_url=_get_optional_env("APP_BASE_URL", "http://localhost:5500") or "http://localhost:5500",
        openai_api_key=_get_optional_env("OPENAI_API_KEY"),
    )


def refresh_settings() -> None:
    """Clear the cached settings so the next call re-reads the environment."""

    get_settings.cache_clear()  # type: ignore[attr-defined]


__all__ = [
    "MissingEnvironmentVariable",
    "Settings",
    "get_settings",
    "refresh_settings",
]
