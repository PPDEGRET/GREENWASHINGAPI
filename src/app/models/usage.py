import uuid
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, func, Integer, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from src.app.db.database import Base

class UsageLog(Base):
    __tablename__ = "usage_logs"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=True)
    ip_address: Mapped[str] = mapped_column(String(50), nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=func.now(), nullable=False)
    # analysis_id is not needed as the id of this table serves the same purpose
    input_type: Mapped[str] = mapped_column(String(50), nullable=False) # "image", "text", "url"
    chars_count: Mapped[int] = mapped_column(Integer, nullable=True)
    premium_features_used: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    result_json: Mapped[dict] = mapped_column(JSON, nullable=False)
    duration_ms: Mapped[int] = mapped_column(Integer, nullable=False)
