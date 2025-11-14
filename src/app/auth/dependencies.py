from typing import Optional
from fastapi import Depends, Request
from src.app.models.user import User
from src.app.routers.auth import fastapi_users

async def get_optional_current_user(request: Request) -> Optional[User]:
    try:
        user = await fastapi_users.authenticator.try_read_user(request)
        return user
    except Exception:
        return None
