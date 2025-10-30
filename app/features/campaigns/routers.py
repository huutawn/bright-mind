from sqlalchemy.ext.asyncio import AsyncSession
from .models import Campaign
from app.helpers.bases import DataResponse
from .schemas import CampaignResponse, CampaignCreationReq, CampaignChoosing
from app.helpers.deps import get_current_user
from app.db.base import get_db
from ..users.models import User
from fastapi import APIRouter, Depends
import json
import redis
import logging
from app.core.redis_client import get_redis_client
from .services import CampaignService
from app.helpers.paging import Page, PaginationParams
from app.helpers.login_manager import permission_required

router = APIRouter()


def get_campaign_service() -> CampaignService:
    return CampaignService()


require_admin_role = permission_required('admin')


@router.post('', response_model=DataResponse[CampaignResponse])
async def create_campaign(data: CampaignCreationReq,
                          user: User = Depends(get_current_user),
                          db: AsyncSession = Depends(get_db),
                          campaign_service: CampaignService = Depends(get_campaign_service)):
    res = await campaign_service.create_campaign(data=data, user=user, db=db)
    return DataResponse(data=res) # No change needed here, but for consistency


@router.get('/all', response_model=Page[CampaignResponse])
async def get_all_campaign(params: PaginationParams = Depends(),
                           db: AsyncSession = Depends(get_db),
                           campaign_service: CampaignService = Depends(get_campaign_service),
                           redis_client: redis.Redis = Depends(get_redis_client)):
    cache_key = f"campaigns:all:page_{params.page}:size_{params.page_size}"
    cached_campaigns = redis_client.get(cache_key)
    if cached_campaigns:
        return Page[CampaignResponse].model_validate(json.loads(cached_campaigns))

    campaigns = await campaign_service.get_all(params, db)
    redis_client.set(cache_key, campaigns.model_dump_json(), ex=600)
    return campaigns


@router.get('/pending', response_model=Page[CampaignResponse])
async def get_all_pending(params: PaginationParams = Depends(),
                          db: AsyncSession = Depends(get_db),
                          campaign_service: CampaignService = Depends(get_campaign_service),
                          redis_client: redis.Redis = Depends(get_redis_client)):
    cache_key = f"campaigns:pending:page_{params.page}:size_{params.page_size}"
    cached_campaigns = redis_client.get(cache_key)
    if cached_campaigns:
        return Page[CampaignResponse].model_validate(json.loads(cached_campaigns))
    
    campaigns = await campaign_service.get_all_pending(params, db)
    redis_client.set(cache_key, campaigns.model_dump_json(), ex=600)
    return campaigns


@router.get('/depended', response_model=Page[CampaignResponse])
async def get_all_depended(params: PaginationParams = Depends(),
                           db: AsyncSession = Depends(get_db),
                           admin: User =Depends(require_admin_role),
                           campaign_service: CampaignService = Depends(get_campaign_service),
                           redis_client: redis.Redis = Depends(get_redis_client)):
    cache_key = f"campaigns:depended:page_{params.page}:size_{params.page_size}"
    cached_campaigns = redis_client.get(cache_key)
    if cached_campaigns:
        return Page[CampaignResponse].model_validate(json.loads(cached_campaigns))

    campaigns: Page[CampaignResponse] = await campaign_service.get_all_depended(params, db,admin=admin)
    redis_client.set(cache_key, campaigns.model_dump_json(), ex=600)
    return campaigns

@router.patch('/choose/{campaign_id}', response_model=DataResponse[CampaignChoosing])
async def choose_campaign(campaign_id: int,
                          db: AsyncSession = Depends(get_db),
                          admin: User = Depends(require_admin_role),
                          campaign_service: CampaignService = Depends(get_campaign_service),
                          redis_client: redis.Redis = Depends(get_redis_client)):
    logging.warning(f"Choosing campaign with ID: {campaign_id}")
    # Invalidate cache for the specific campaign and lists
    redis_client.delete(f"campaign:{campaign_id}")
    # A more robust approach is to use key patterns
    for key in redis_client.scan_iter("campaigns:all:*"):
        redis_client.delete(key)
    res = await campaign_service.choose_campaign(campaign_id=campaign_id, db=db, admin=admin)
    return DataResponse(data=res)

@router.patch('/approve/{campaign_id}', response_model=DataResponse[CampaignChoosing])
async def approve_campaign(campaign_id: int,
                           db: AsyncSession = Depends(get_db),
                           admin: User = Depends(require_admin_role),
                           campaign_service: CampaignService = Depends(get_campaign_service),
                           redis_client: redis.Redis = Depends(get_redis_client)):
    # Invalidate cache for the specific campaign and lists
    redis_client.delete(f"campaign:{campaign_id}")
    # Invalidate all paginated results as status has changed
    for key in redis_client.scan_iter("campaigns:*"):
        redis_client.delete(key)
    res = await campaign_service.approve_campaign(campaign_id=campaign_id, db=db)
    return DataResponse(data=res)


@router.get('/detail/{campaign_id}',response_model=DataResponse[CampaignResponse])
async def get_detail(campaign_id: int,
                     db: AsyncSession = Depends(get_db),
                     campaign_service: CampaignService = Depends(get_campaign_service),
                     redis_client: redis.Redis = Depends(get_redis_client)):
    cache_key = f"campaign:{campaign_id}"
    cached_campaign = redis_client.get(cache_key)
    if cached_campaign:
        campaign = CampaignResponse.model_validate(json.loads(cached_campaign))
        return DataResponse(data=campaign)
    res = await campaign_service.get_detail(campaign_id=campaign_id, db=db)
    redis_client.set(cache_key, res.model_dump_json(), ex=600)
    return DataResponse(data=res)

@router.get('/current',response_model=Page[CampaignResponse])
async def get_campaigns_by_current_admin(params: PaginationParams = Depends(),
                                         db: AsyncSession = Depends(get_db),
                                         admin: User = Depends(require_admin_role),
                                         campaign_service: CampaignService = Depends(get_campaign_service),
                                         redis_client: redis.Redis = Depends(get_redis_client)):
    cache_key = f"campaigns:current_admin_{admin.id}:page_{params.page}:size_{params.page_size}"
    cached_campaigns = redis_client.get(cache_key)
    if cached_campaigns:
        return Page[CampaignResponse].model_validate(json.loads(cached_campaigns))

    res = await campaign_service.get_campaign_by_current_admin(params,db,admin)
    redis_client.set(cache_key, res.model_dump_json(), ex=600)
    return res