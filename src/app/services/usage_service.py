from datetime import datetime, timedelta
from sqlalchemy import select, func
from src.app.db.database import async_session_maker
from src.app.models.user import User
from src.app.models.usage import UsageLog

NON_PREMIUM_LIMIT = 3

async def log_analysis(user: User, input_type: str, result_json: dict, duration_ms: int):
    async with async_session_maker() as session:
        usage_log = UsageLog(
            user_id=user.id,
            input_type=input_type,
            result_json=result_json,
            duration_ms=duration_ms,
            premium_features_used=user.is_premium
        )
        session.add(usage_log)
        await session.commit()

async def can_user_perform_analysis(user: User) -> bool:
    if user.is_premium:
        return True

    async with async_session_maker() as session:
        today = datetime.utcnow().date()
        start_of_day = datetime.combine(today, datetime.min.time())

        result = await session.execute(
            select(func.count(UsageLog.id))
            .where(UsageLog.user_id == user.id)
            .where(UsageLog.timestamp >= start_of_day)
        )
        count = result.scalar_one_or_none() or 0
        return count < NON_PREMIUM_LIMIT

async def get_usage_history(user: User):
    async with async_session_maker() as session:
        result = await session.execute(
            select(UsageLog).where(UsageLog.user_id == user.id).order_by(UsageLog.timestamp.desc())
        )
        return result.scalars().all()

async def get_usage_log_by_id(user: User, log_id: str):
    async with async_session_maker() as session:
        result = await session.execute(
            select(UsageLog).where(UsageLog.user_id == user.id, UsageLog.id == log_id)
        )
        return result.scalar_one_or_none()
