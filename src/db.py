# src/db.py
from __future__ import annotations

from supabase import Client, create_client

from config import MissingEnvironmentVariable, get_settings


def _base_client() -> Client:
    settings = get_settings()
    return create_client(settings.supabase_url, settings.supabase_anon_key)


def supabase_client() -> Client:
    """Non-authed client (anon key). Use only for public tables."""

    return _base_client()


def supabase_admin() -> Client:
    """Service-role client (server-only). Avoid using unless doing admin tasks."""

    settings = get_settings()
    service_role = settings.supabase_service_role
    if not service_role:
        raise MissingEnvironmentVariable("SUPABASE_SERVICE_ROLE")
    return create_client(settings.supabase_url, service_role)


def supabase_user_client(access_token: str | None) -> Client:
    """
    Client that carries the user's JWT so RLS sees auth.uid().
    Use this for all reads/writes on RLS-protected tables.
    """

    client = _base_client()
    if access_token:
        # Attach the token to both PostgREST and Auth subclients
        try:
            client.postgrest.auth(access_token)
        except Exception:
            pass
        try:
            client.auth.set_auth(access_token)
        except Exception:
            pass
    return client


def get_app_base_url() -> str:
    """Return the base URL where the Streamlit app is exposed."""

    return get_settings().app_base_url


APP_BASE_URL = get_app_base_url()

__all__ = [
    "APP_BASE_URL",
    "get_app_base_url",
    "supabase_admin",
    "supabase_client",
    "supabase_user_client",
]
