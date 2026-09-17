"""Developer lookup + specialist matching."""
from app.services.base import db


def list_developers(active_only: bool = True) -> list[dict]:
    query = db().table("developers").select("*")
    if active_only:
        query = query.eq("active", True)
    return query.execute().data


def get_developer(developer_id: str) -> dict | None:
    result = db().table("developers").select("*").eq("id", developer_id).execute()
    return result.data[0] if result.data else None
def get_developer_by_email(email: str) -> dict | None:
    result = db().table("developers").select("*").eq("email", email).execute()
    return result.data[0] if result.data else None


def find_specialist(technology: str | None) -> dict | None:
    """
    Very simple keyword match against `specialty`. Good enough for an MVP;
    a real version might use a join table (see proposal doc) or embeddings.
    """
    developers = list_developers(active_only=True)
    if not technology:
        return developers[0] if developers else None
    technology_lower = technology.lower()
    for dev in developers:
        if dev.get("specialty") and technology_lower in dev["specialty"].lower():
            return dev
    return developers[0] if developers else None
