import os
from fastapi_users.authentication import AuthenticationBackend, JWTStrategy

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("SECRET_KEY not found in environment variables")

def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=SECRET_KEY, lifetime_seconds=3600)

auth_backend = AuthenticationBackend(
    name="jwt",
    transport=None, # This will be set in the router
    get_strategy=get_jwt_strategy,
)
