from fastapi import Depends, HTTPException, status
from src.app.models.user import User
from src.app.routers.auth import current_user

async def get_premium_user(user: User = Depends(current_user)) -> User:
    if not user.is_premium:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This feature is only available to premium users.",
        )
    return user
