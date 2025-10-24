# src/db.py
import os
from supabase import create_client, Client

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
SUPABASE_SERVICE_ROLE = os.getenv("SUPABASE_SERVICE_ROLE")
APP_BASE_URL = os.getenv("APP_BASE_URL", "http://localhost:8501")

def _assert_env():
    missing = []
    if not SUPABASE_URL:
        missing.append("SUPABASE_URL")
    if not SUPABASE_ANON_KEY:
        missing.append("SUPABASE_ANON_KEY")
    if missing:
        raise RuntimeError(f"Missing env vars: {', '.join(missing)}")

def supabase_client() -> Client:
    """Non-authed client (anon key). Use only for public tables or admin ops with service role."""
    _assert_env()
    return create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

def supabase_admin() -> Client:
    """Service-role client (server-only). Avoid using unless doing admin tasks."""
    _assert_env()
    if not SUPABASE_SERVICE_ROLE:
        raise RuntimeError("SUPABASE_SERVICE_ROLE is required for admin client")
    return create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE)

def supabase_user_client(access_token: str | None) -> Client:
    """
    Client that carries the user's JWT so RLS sees auth.uid().
    Use this for all reads/writes on RLS-protected tables.
    """
    _assert_env()
    client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
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
