import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Request
from src.app.models.user import User
from src.app.auth.dependencies import get_optional_current_user
from src.app.routers.auth import current_user
from src.app.services import usage_service
from src.app.schemas.usage import UsageLogRead, UsageSummary

router = APIRouter()


@router.get("/usage/summary", response_model=UsageSummary)
async def get_usage_summary_endpoint(
    request: Request,
    user: Optional[User] = Depends(get_optional_current_user),
):
    ip_address = request.client.host
    summary = await usage_service.get_usage_summary(user=user, ip_address=ip_address)
    return summary


@router.get("/me/usage", response_model=List[UsageLogRead])
async def get_my_usage(user: User = Depends(current_user)):
    return await usage_service.get_usage_history(user)

@router.get("/me/usage/{log_id}", response_model=UsageLogRead)
async def get_my_usage_log(log_id: uuid.UUID, user: User = Depends(current_user)):
    log = await usage_service.get_usage_log_by_id(user, log_id)
    if not log:
        raise HTTPException(status_code=404, detail="Usage log not found")
    return log
