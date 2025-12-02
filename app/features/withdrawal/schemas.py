from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from decimal import Decimal
# Withdrawal Schemas
class WithdrawalBase(BaseModel):
    id: int
    campaign_id: int
    amount: Decimal
    type: Optional[str] = 'normal'
    status: Optional[str] = 'pending'
    reason: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


class WithdrawalResponse(WithdrawalBase):
    approved_at: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


class WithdrawalCreateReq(BaseModel):
    campaign_id: int
    amount: Decimal
    type: Optional[str] = 'normal'
    reason: Optional[str] = None


# Proof Schemas
class ProofBase(BaseModel):
    id: int
    withdrawal_id: int
    description: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


class ProofResponse(ProofBase):
    ai_validated_amount: Optional[Decimal] = None
    ai_validation_status: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


class ProofCreateReq(BaseModel):
    withdrawal_id: int
    description: Optional[str] = None


# ProofImage Schemas
class ProofImageBase(BaseModel):
    id: int
    proof_id: int
    image_url: str
    model_config = ConfigDict(from_attributes=True)


class ProofImageResponse(ProofImageBase):
    model_config = ConfigDict(from_attributes=True)


class ProofImageCreateReq(BaseModel):
    proof_id: int
    image_url: str