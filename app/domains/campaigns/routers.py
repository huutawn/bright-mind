from sqlalchemy.ext.asyncio import AsyncSession
from .models import Campaign
from app.helpers.bases import DataResponse
from .schemas import CampaignResponse, CampaignCreationReq, CampaignChoosing
from app.helpers.deps import get_current_user
from app.db.base import get_db
from ..users.models import User
from fastapi import APIRouter, Depends
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
    return DataResponse(data=res)


@router.get('/all', response_model=Page[CampaignResponse])
async def get_all_campaign(params: PaginationParams = Depends(),
                           db: AsyncSession = Depends(get_db),
                           campaign_service: CampaignService = Depends(get_campaign_service)):
    campaigns = await campaign_service.get_all(params, db)
    return campaigns


@router.get('/pending', response_model=Page[CampaignResponse])
async def get_all_pending(params: PaginationParams = Depends(),
                          db: AsyncSession = Depends(get_db),
                          campaign_service: CampaignService = Depends(get_campaign_service)):
    campaigns = await campaign_service.get_all_pending(params, db)
    return campaigns


@router.get('/depended', response_model=Page[CampaignResponse])
async def get_all_depended(params: PaginationParams = Depends(),
                           db: AsyncSession = Depends(get_db),
                           campaign_service: CampaignService = Depends(get_campaign_service)):
    campaigns = await campaign_service.get_all_depended(params, db)
    return campaigns
