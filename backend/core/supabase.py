from supabase import create_client, Client
from core.config import settings

_supabase_client: Client | None = None


def get_supabase() -> Client:
    """Get or create a Supabase client instance (singleton)."""
    global _supabase_client

    if _supabase_client is None:
        if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
            raise RuntimeError(
                "Supabase is not configured. "
                "Set SUPABASE_URL and SUPABASE_KEY in your .env file."
            )

        _supabase_client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_KEY,
        )
        print("✅ Supabase client initialized successfully.")

    return _supabase_client
