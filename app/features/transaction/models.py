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

    


class Withdrawal(BareBaseModel):
    campaign: Mapped['Campaign'] = relationship(back_populates='withdrawal')
    campaign_id: Mapped[int] = mapped_column(ForeignKey('campaign.id'))
    amount: Mapped[Decimal] = mapped_column(DECIMAL(12, 2))
    type: Mapped[Optional[str]] = mapped_column(String, default='normal')
    status: Mapped[Optional[str]] = mapped_column(String, default='pending')
    reason: Mapped[Optional[str]] = mapped_column(Text)
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    proof: Mapped[Optional[List['Proof']]] = relationship(back_populates='withdrawal', cascade='all, delete-orphan', foreign_keys='Proof.withdrawal_id')

    


class Proof(BareBaseModel):
    withdrawal_id: Mapped[int] = mapped_column(ForeignKey('withdrawal.id'))
    withdrawal: Mapped['Withdrawal'] = relationship(back_populates='proof',foreign_keys='Proof.withdrawal_id')
    proof_image: Mapped[List['ProofImage']] = relationship(back_populates='proof', cascade='all, delete-orphan')
    description: Mapped[Optional[str]] = mapped_column(Text)
    ai_validated_amount: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(12, 2))
    ai_validation_status: Mapped[Optional[str]] = mapped_column(String)

    


class ProofImage(BareBaseModel):
    image_url: Mapped[str] = mapped_column(String(200))
    proof: Mapped['Proof'] = relationship(back_populates='proof_image')
    proof_id: Mapped[int] = mapped_column(ForeignKey('proof.id'))

    

class TransactionError(BareBaseModel):
    bank_name: Mapped[Optional[str]] = mapped_column(String)
    bank_number: Mapped[Optional[str]] = mapped_column(String)
    amount: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(12,2))
    content: Mapped[Optional[str]] = mapped_column(String)
    status: Mapped[Optional[str]] = mapped_column(String, default='pending')

    
    