from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from .models import Campaign
from decimal import Decimal
from datetime import date, timedelta
from .schemas import CampaignResponse, CampaignCreationReq, CampaignChoosing
from app.helpers.exception_handler import CustomException, ExceptionType
from app.helpers.paging import PaginationParams, paginate
from ..users.models import User
from .mappers import CampaignMapper
from app.helpers.enums import CampaignStatus

class CampaignService:
    def __init__(self):
        pass

    async def create_campaign(self,data: CampaignCreationReq, db: AsyncSession, user: User) -> CampaignResponse:
        if user.status == 'banned':
            raise CustomException(ExceptionType.USER_BANNED)
        campaign = Campaign(
            title=data.title,
            description = data.description,
            cover_image_url = data.cover_image_url,
            goal_amount = data.goal_amount,
            end_date = self.calculate_end_date(data.goal_amount),
            creator = user,
            creator_id = user.id,
        )
        db.add(campaign)
        await db.commit()
        await db.refresh(campaign)
        return CampaignMapper.toCampaignResponse(campaign)

    async def get_all(self,params: PaginationParams, db: AsyncSession):
        _query = select(Campaign).options(
            selectinload(Campaign.creator)
        ).filter(Campaign.status == CampaignStatus.APPROVED.value)
        mapper = CampaignMapper.toCampaignResponse

        campaigns = await paginate(db=db,
                                   model=Campaign,
                                   query=_query,
                                   mapper=mapper,
                                   params=params)
        return campaigns

    async def get_all_pending(self, params: PaginationParams, db: AsyncSession):
        _query = select(Campaign).options(
            selectinload(Campaign.creator)
        ).filter(Campaign.status == CampaignStatus.PENDING.value)
        mapper = CampaignMapper.toCampaignResponse

        campaigns = await paginate(db=db,
                                   model=Campaign,
                                   query=_query,
                                   mapper=mapper,
                                   params=params)
        return campaigns

    async def get_all_depended(self, params: PaginationParams,
                               db: AsyncSession):
        _query = select(Campaign).options(
            selectinload(Campaign.creator)
        ).filter(Campaign.status == CampaignStatus.DEPENDED.value)
        mapper = CampaignMapper.toCampaignResponse

        campaigns = await paginate(db=db,
                                   model=Campaign,
                                   query=_query,
                                   mapper=mapper,
                                   params=params)
        return campaigns
    async def choose_campaign(self,campaign_id: int,
                              db: AsyncSession,
                              admin: User
                              ) -> CampaignChoosing:
        campaign: Campaign | None = await db.get(Campaign, campaign_id)
        if not campaign:
            raise CustomException(ExceptionType.CAMPAIGN_NOT_FOUND)
        campaign.status=CampaignStatus.DEPENDED.value
        admin.campaign_depended.append(campaign)
        db.add(admin)
        await db.commit()
        return CampaignChoosing(
            campaign_id=campaign.id,
            status=campaign.status,
        )




    def calculate_end_date(self, amount: Decimal) -> date:

        BASE_DAYS = 30

        ACCELERATION_THRESHOLD = Decimal('100000000')


        ACCELERATION_FACTOR = 10



        additional_days = 0
        if amount >= ACCELERATION_THRESHOLD:
            num_increments = int(amount // ACCELERATION_THRESHOLD)

            additional_days = ACCELERATION_FACTOR * (num_increments ** 2)

        total_days = BASE_DAYS + additional_days

        today = date.today()
        future_date = today + timedelta(days=int(total_days))

        return future_date




