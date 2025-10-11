from .models import Campaign
from .schemas import CampaignResponse
from ..users.mappers import UserMapper

class CampaignMapper:
    @staticmethod
    def toCampaignResponse(campaign: Campaign):
       return CampaignResponse.model_validate(campaign)

