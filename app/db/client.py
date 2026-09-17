"""
Supabase client singleton.

We use the service_role key here (NOT the anon key) because this is a
trusted backend server, not a browser. The service_role key bypasses
row-level security, which is fine because our FastAPI layer is the one
enforcing access rules — never expose this key to the frontend.
"""

from supabase import create_client, Client

from app.config import settings

_client: Client | None = None


def get_supabase() -> Client:
    """Return a lazily-created, reused Supabase client."""
    global _client
    if _client is None:
        if not settings.SUPABASE_URL or not settings.SUPABASE_SERVICE_ROLE_KEY:
            raise RuntimeError(
                "SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set in .env "
                "before the database can be used."
            )
        _client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)
    return _client
