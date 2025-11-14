import uuid
from fastapi import APIRouter, Depends
from fastapi_users import FastAPIUsers
from fastapi_users.authentication import CookieTransport

from src.app.auth.manager import get_user_manager
from src.app.auth.transport import auth_backend
from src.app.models.user import User
from src.app.auth.schemas import UserRead, UserCreate, UserUpdate

cookie_transport = CookieTransport(cookie_name="greencheck", cookie_max_age=3600)
auth_backend.transport = cookie_transport

fastapi_users = FastAPIUsers[User, uuid.UUID](
    get_user_manager,
    [auth_backend],
)

router = APIRouter()

router.include_router(
    fastapi_users.get_auth_router(auth_backend), prefix="/auth/jwt", tags=["auth"]
)
router.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)
router.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/auth",
    tags=["auth"],
)
router.include_router(
    fastapi_users.get_verify_router(UserRead),
    prefix="/auth",
    tags=["auth"],
)
router.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
)

current_user = fastapi_users.current_user()

@router.get("/users/me", response_model=UserRead)
async def authenticated_route(user: User = Depends(current_user)):
    return user
