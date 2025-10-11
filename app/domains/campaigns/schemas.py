from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict
from decimal import Decimal
from ..users.schemas import UserResponse

class CampaignBase(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    cover_image_url: Optional[str] =None
    goal_amount: Decimal
    start_date: Optional[date]
    model_config = ConfigDict(from_attributes=True)
class CampaignChoosing(BaseModel):
    campaign_id: int
    status: str
    model_config = ConfigDict(from_attributes=True)
class CampaignCreationReq(CampaignBase):
    title: str

class CampaignResponse(CampaignBase):
    id: int
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    status: str
    current_amount: Optional[Decimal]
    used_amount: Optional[Decimal]
    creator: Optional['UserResponse']
    end_date: Optional[date]
    quickly_used: bool
