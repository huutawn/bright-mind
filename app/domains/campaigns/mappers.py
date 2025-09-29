from .models import Campaign
from .schemas import CampaignResponse
from ..users.mappers import UserMapper

class CampaignMapper:
    @staticmethod
    def toCampaignResponse(campaign: Campaign):
        return CampaignResponse(
            id=campaign.id,
            title=campaign.title,
            description=campaign.description,
            current_amount=campaign.current_amount,
            cover_image_url=campaign.cover_image_url,
            goal_amount=campaign.goal_amount,
            used_amount=campaign.used_amount,
            status=campaign.status,
            start_date=campaign.start_date,
            end_date=campaign.end_date,
            creator=UserMapper.to_user_response(campaign.creator),
            created_at=campaign.created_at,
            updated_at=campaign.updated_at
        )

