"""
Auth dependency: verifies a Supabase JWT from the Authorization header,
returns the user's role. Used to protect admin-only routes.
"""
from fastapi import Depends, Header, HTTPException
from app.db.client import get_supabase


def get_current_user(authorization: str = Header(...)):
    token = authorization.replace("Bearer ", "")
    try:
        result = get_supabase().auth.get_user(token)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    if not result or not result.user:
        raise HTTPException(status_code=401, detail="Invalid token")
    role = result.user.user_metadata.get("role", "employee")
    return {"id": result.user.id, "email": result.user.email, "role": role}


def require_admin(user: dict = Depends(get_current_user)):
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return user