from fastapi import APIRouter, Depends, Request

from app.core.payos_client import get_payos_client
from payos import PayOS
from typing import Any
from .services import DonationService
from app.helpers.deps import get_current_user, get_current_user_optional
from app.helpers.bases import DataResponse
from app.helpers.paging import Page, PaginationParams
from app.features.transaction.models import Donation
from app.features.users.models import User
from app.helpers.login_manager import permission_required
from app.db.base import get_db
import json
import redis
from app.core.redis_client import get_redis_client
from app.features.transaction.schemas import (
    DonationReq,
    DonationResponse,
)
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


def get_donation_service() -> DonationService:
    return DonationService()


@router.post("/donation", response_model=DataResponse[Any])
async def create_donation(
    data: DonationReq,
    db: AsyncSession = Depends(get_db),
    donation_service: DonationService = Depends(get_donation_service),
    user: User | None = Depends(get_current_user_optional),
    payos_client: PayOS = Depends(get_payos_client),
):
    res = await donation_service.create_donation(data, db, user, payos_client)
    return DataResponse(data=res)


@router.get("/donation", response_model=Page[DonationResponse])
async def get_all_donation(
    db: AsyncSession = Depends(get_db),
    donation_service: DonationService = Depends(get_donation_service),
    user: User = Depends(get_current_user_optional),
    params: PaginationParams = Depends(),
    redis_client: redis.Redis = Depends(get_redis_client),
):
    cache_key = f"donation:page_{params.page}:size_{params.page_size}"
    cached_donations =  redis_client.get(cache_key)
    if cached_donations:
        return Page[DonationResponse].model_validate(json.loads(cached_donations))
    res = await donation_service.get_all_donation(db, user, params)
    redis_client.set(cache_key, res.model_dump_json(), ex=600)
    return res


@router.get("/donation/campaign/{campaign_id}", response_model=Page[DonationResponse])
async def get_all_donation_by_campaign(
    campaign_id: int,
    db: AsyncSession = Depends(get_db),
    donation_service: DonationService = Depends(get_donation_service),
    params: PaginationParams = Depends(),
    redis_client: redis.Redis = Depends(get_redis_client),
):
    cache_key = (
        f"donation:campaign_{campaign_id}:page_{params.page}:size_{params.page_size}"
    )
    cached_donations = await redis_client.get(cache_key)
    if cached_donations:
        return Page[DonationResponse].model_validate(json.loads(cached_donations))

    res = await donation_service.get_all_donation_by_campaign(campaign_id, params, db)
    redis_client.set(cache_key, res.model_dump_json(), ex=600)
    return res



@router.post("/webhooks", response_model=DataResponse[DonationResponse])
async def webhooks(
    data: Request,
    db: AsyncSession = Depends(get_db),
    service: DonationService = Depends(get_donation_service),
    payos_client: PayOS = Depends(get_payos_client),
):
    res = await service.transaction_handler(data, db, payos_client)
    return DataResponse(data=res)
