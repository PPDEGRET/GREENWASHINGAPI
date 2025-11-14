import uuid
from datetime import datetime
from typing import List
from sqlalchemy import String, Boolean, DateTime, func, JSON
from sqlalchemy.orm import Mapped, mapped_column
from fastapi_users.db import SQLAlchemyBaseUserTableUUID
from src.app.db.database import Base

class User(SQLAlchemyBaseUserTableUUID, Base):
    __tablename__ = "users"

    # Fields from FastAPI-Users
    # id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    # email: Mapped[str] = mapped_column(String(320), unique=True, index=True, nullable=False)
    # hashed_password: Mapped[str] = mapped_column(String(1024), nullable=False)
    # is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    # is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    # is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Custom fields
    is_premium: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), nullable=False)
    last_login_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    # Onboarding data
    company_name: Mapped[str] = mapped_column(String(100), nullable=True)
    sector: Mapped[str] = mapped_column(String(100), nullable=True)
    company_size: Mapped[str] = mapped_column(String(50), nullable=True)
    country: Mapped[str] = mapped_column(String(100), nullable=True)
    role: Mapped[str] = mapped_column(String(100), nullable=True)
    use_cases: Mapped[List[str]] = mapped_column(JSON, nullable=True)
    custom_needs: Mapped[str] = mapped_column(String(500), nullable=True)
