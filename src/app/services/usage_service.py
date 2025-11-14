from datetime import datetime
from typing import Optional
from fastapi import Request
from sqlalchemy import select, func
from src.app.db.database import async_session_maker
from src.app.models.user import User
from src.app.models.usage import UsageLog

# Daily free analysis limit for non-premium users (per user/IP).
# Local development (127.0.0.1) is exempt from this limit so you can test freely.
NON_PREMIUM_LIMIT = 3


async def log_analysis(
    input_type: str,
    result_json: dict,
    duration_ms: int,
    user: Optional[User] = None,
    ip_address: Optional[str] = None,
):
    async with async_session_maker() as session:
        usage_log = UsageLog(
            user_id=user.id if user else None,
            ip_address=ip_address,
            input_type=input_type,
            result_json=result_json,
            duration_ms=duration_ms,
            premium_features_used=user.is_premium if user else False,
        )
        session.add(usage_log)
        await session.commit()

async def _get_daily_usage_count(user: Optional[User] = None, ip_address: Optional[str] = None) -> int:
    """Return how many analyses have been performed today by this user/IP."""
    async with async_session_maker() as session:
        today = datetime.utcnow().date()
        start_of_day = datetime.combine(today, datetime.min.time())

        query = select(func.count(UsageLog.id)).where(UsageLog.timestamp >= start_of_day)

        if user:
            query = query.where(UsageLog.user_id == user.id)
        elif ip_address:
            query = query.where(UsageLog.ip_address == ip_address)
        else:
            # If we somehow don't have user or IP, treat as zero for display purposes.
            return 0

        result = await session.execute(query)
        return result.scalar_one_or_none() or 0


async def can_perform_analysis(user: Optional[User] = None, ip_address: Optional[str] = None) -> bool:
    # Premium users have no limit
    if user and user.is_premium:
        return True

    # Allow unlimited usage from localhost during development so you don't get blocked
    # while testing the app locally.
    if ip_address in {"127.0.0.1", "localhost"}:
        return True

    count = await _get_daily_usage_count(user=user, ip_address=ip_address)
    return count < NON_PREMIUM_LIMIT


async def get_usage_summary(user: Optional[User] = None, ip_address: Optional[str] = None) -> dict:
    """Return a simple summary of today's usage for display in the UI."""
    is_premium = bool(user and user.is_premium)
    count = await _get_daily_usage_count(user=user, ip_address=ip_address)

    return {
        "used_today": int(count),
        "remaining_today": max(0, NON_PREMIUM_LIMIT - int(count)),
        "limit": NON_PREMIUM_LIMIT,
        "is_premium": is_premium,
    }


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
