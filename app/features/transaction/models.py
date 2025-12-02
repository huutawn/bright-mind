from app.helpers.bases import BareBaseModel
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Boolean, String, DECIMAL, func, ForeignKey, Text, DateTime
from typing import Optional, List
from decimal import Decimal
from datetime import datetime


class Donation(BareBaseModel):
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey('user.id'))
    user: Mapped[Optional['User']] = relationship(back_populates='donation',foreign_keys='Donation.user_id')
    user_name: Mapped[Optional[str]] = mapped_column(String)
    anonymous_name: Mapped[Optional[str]] = mapped_column(String)
    campaign_id: Mapped[Optional[int]] = mapped_column(ForeignKey('campaign.id'))
    campaign: Mapped[Optional['Campaign']] = relationship(back_populates='donation',foreign_keys='Donation.campaign_id')
    amount: Mapped[Decimal] = mapped_column(DECIMAL(12, 2))
    message: Mapped[str] = mapped_column(String(255))
    transaction_id: Mapped[Optional[str]] = mapped_column(String(255))
    bank_number: Mapped[Optional[str]] = mapped_column(String)
    bank_name: Mapped[Optional[str]] = mapped_column(String)
    status: Mapped[str] = mapped_column(String, default='pending')
    code: Mapped[Optional[str]] = mapped_column(String)


class TransactionError(BareBaseModel):
    bank_name: Mapped[Optional[str]] = mapped_column(String)
    bank_number: Mapped[Optional[str]] = mapped_column(String)
    amount: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(12,2))
    content: Mapped[Optional[str]] = mapped_column(String)
    status: Mapped[Optional[str]] = mapped_column(String, default='pending')

    
    