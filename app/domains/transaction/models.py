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

    def __init__(self, campaign_id: int, message: str, amount: Decimal = Decimal('0.00'),
                 user_id: Optional[int] = None, user_name: Optional[str] = None,
                 anonymous_name: Optional[str] = None, transaction_id: Optional[str] = None,
                 bank_number: Optional[str] = None, bank_name: Optional[str] = None,
                 status: str = 'pending', code: Optional[str] = None):
        self.campaign_id = campaign_id
        self.message = message
        self.amount = amount
        self.user_id = user_id
        self.user_name = user_name
        self.anonymous_name = anonymous_name
        self.transaction_id = transaction_id
        self.bank_number = bank_number
        self.bank_name = bank_name
        self.status = status
        self.code = code


class Withdrawal(BareBaseModel):
    campaign: Mapped['Campaign'] = relationship(back_populates='withdrawal')
    campaign_id: Mapped[int] = mapped_column(ForeignKey('campaign.id'))
    amount: Mapped[Decimal] = mapped_column(DECIMAL(12, 2))
    type: Mapped[Optional[str]] = mapped_column(String, default='normal')
    status: Mapped[Optional[str]] = mapped_column(String, default='pending')
    reason: Mapped[Optional[str]] = mapped_column(Text)
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    proof: Mapped[Optional[List['Proof']]] = relationship(back_populates='withdrawal', cascade='all, delete-orphan', foreign_keys='Proof.withdrawal_id')

    def __init__(self, campaign_id: int, amount: Decimal, type: str = 'normal',
                 status: str = 'pending', reason: Optional[str] = None,
                 approved_at: Optional[datetime] = None):
        self.campaign_id = campaign_id
        self.amount = amount
        self.type = type
        self.status = status
        self.reason = reason
        self.approved_at = approved_at


class Proof(BareBaseModel):
    withdrawal_id: Mapped[int] = mapped_column(ForeignKey('withdrawal.id'))
    withdrawal: Mapped['Withdrawal'] = relationship(back_populates='proof',foreign_keys='Proof.withdrawal_id')
    proof_image: Mapped[List['ProofImage']] = relationship(back_populates='proof', cascade='all, delete-orphan')
    description: Mapped[Optional[str]] = mapped_column(Text)
    ai_validated_amount: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(12, 2))
    ai_validation_status: Mapped[Optional[str]] = mapped_column(String)

    def __init__(self, withdrawal_id: int, description: Optional[str] = None,
                 ai_validated_amount: Optional[Decimal] = None,
                 ai_validation_status: Optional[str] = None):
        self.withdrawal_id = withdrawal_id
        self.description = description
        self.ai_validated_amount = ai_validated_amount
        self.ai_validation_status = ai_validation_status


class ProofImage(BareBaseModel):
    image_url: Mapped[str] = mapped_column(String(200))
    proof: Mapped['Proof'] = relationship(back_populates='proof_image')
    proof_id: Mapped[int] = mapped_column(ForeignKey('proof.id'))

    def __init__(self, proof_id: int, image_url: str):
        self.proof_id = proof_id
        self.image_url = image_url

class TransactionError(BareBaseModel):
    bank_name: Mapped[Optional[str]] = mapped_column(String)
    bank_number: Mapped[Optional[str]] = mapped_column(String)
    amount: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(12,2))
    content: Mapped[Optional[str]] = mapped_column(String)
    status: Mapped[Optional[str]] = mapped_column(String, default='pending')

    def __init__(self, bank_name: Optional[str] = None, bank_number: Optional[str] = None,
                 amount: Optional[Decimal] = None, content: Optional[str] = None,
                 status: str = 'pending'):
        self.bank_name = bank_name
        self.bank_number = bank_number
        self.amount = amount
        self.content = content
        self.status = status
    