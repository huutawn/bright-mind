import enum


class UserRole(enum.Enum):
    ADMIN = 'admin'
    GUEST = 'guest'

class CampaignStatus(enum.Enum):
    PENDING = 'pending'
    DEPENDED = 'depended'
    APPROVED = 'approved'
    EXPIRED = 'expired'
    ENOUGH = 'enough'
class UserStatus(enum.Enum):
    BANNED = 'banned'
