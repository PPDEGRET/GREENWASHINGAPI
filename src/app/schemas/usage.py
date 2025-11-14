import uuid
from datetime import datetime
from pydantic import BaseModel

class UsageLogRead(BaseModel):
    id: uuid.UUID
    timestamp: datetime
    input_type: str
    chars_count: int | None
    premium_features_used: bool
    result_json: dict
    duration_ms: int

    class Config:
        orm_mode = True


class UsageSummary(BaseModel):
    used_today: int
    remaining_today: int
    limit: int
    is_premium: bool
