import uuid
from typing import Optional, List
from pydantic import BaseModel, EmailStr
from fastapi_users import schemas


class UserRead(schemas.BaseUser[uuid.UUID]):
    is_premium: bool
    company_name: Optional[str] = None
    sector: Optional[str] = None
    company_size: Optional[str] = None
    country: Optional[str] = None
    role: Optional[str] = None
    use_cases: Optional[List[str]] = None
    custom_needs: Optional[str] = None


class UserCreate(schemas.BaseUserCreate):
    pass


class UserUpdate(schemas.BaseUserUpdate):
    is_premium: Optional[bool] = None
    company_name: Optional[str] = None
    sector: Optional[str] = None
    company_size: Optional[str] = None
    country: Optional[str] = None
    role: Optional[str] = None
    use_cases: Optional[List[str]] = None
    custom_needs: Optional[str] = None
