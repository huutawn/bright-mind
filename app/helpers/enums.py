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


class DonateStatus(enum.Enum):
    PENDING = 'pending'
    COMPLETE = 'complete'
    
class WithdrawalStatus(enum.Enum):
    PENDING = 'pending'
    WAITING = 'waiting'
    PROVEN = 'proven'

