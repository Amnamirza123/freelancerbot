"""Small helpers shared by every service module."""
from app.db.client import get_supabase


def db():
    return get_supabase()
