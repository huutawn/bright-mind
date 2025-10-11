from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, DateTime, Date, Boolean, Text, DECIMAL, func, ForeignKey
from typing import Optional, List
from app.helpers.bases import BareBaseModel
from decimal import Decimal
from datetime import datetime, date
from app.helpers.enums import CampaignStatus

class Campaign(BareBaseModel):
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text)
    cover_image_url: Mapped[str] = mapped_column(String(150))
    goal_amount: Mapped[Decimal] = mapped_column(DECIMAL(12,2))
    current_amount: Mapped[Decimal] = mapped_column(DECIMAL(12,2), default=Decimal('0.00'))
    used_amount: Mapped[Decimal] = mapped_column(DECIMAL(12,2), default=Decimal('0.00'))
    status: Mapped[str] = mapped_column(String(20), default=CampaignStatus.PENDING.value)
    start_date: Mapped[date] = mapped_column(Date(),server_default=func.current_date())
    end_date: Mapped[date] = mapped_column(Date)
    creator: Mapped['User'] = relationship(back_populates='campaign',foreign_keys='Campaign.creator_id')
    creator_id: Mapped[int] = mapped_column(ForeignKey('user.id'))
    user_depend_on: Mapped[Optional['User']] = relationship(back_populates='campaign_depended',foreign_keys='Campaign.user_depend_id')
    user_depend_id: Mapped[Optional[int]] = mapped_column(ForeignKey('user.id'),nullable=True)
    quickly_used: Mapped[Optional[bool]] = mapped_column(Boolean, default=False)
    donation: Mapped[Optional[List['Donation']]] = relationship(back_populates='campaign',cascade='all')
    code: Mapped[Optional[str]] = mapped_column(String)
    withdrawal: Mapped[Optional[List['Withdrawal']]] = relationship(back_populates='campaign',cascade='all', foreign_keys='Withdrawal.campaign_id')
    
