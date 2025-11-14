from fastapi import APIRouter, Depends
from src.app.models.user import User
from src.app.routers.auth import current_user
from src.app.auth.schemas import UserUpdate
from src.app.auth.manager import get_user_manager

router = APIRouter()

@router.post("/me/onboarding", response_model=UserUpdate)
async def complete_onboarding(
    onboarding_data: UserUpdate,
    user: User = Depends(current_user),
    user_manager = Depends(get_user_manager),
):
    user = await user_manager.update_user(user, onboarding_data)
    return user
