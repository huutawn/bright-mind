from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from decimal import Decimal


class WebhookData(BaseModel):
    accountNumber: str
    amount: int
    description: str
    reference: str
    transactionDateTime: str 
    orderCode: int
    currency: str
    paymentLinkId: str
    code: str
    desc: str
    
    virtualAccountNumber: Optional[str] = None
    counterAccountBankId: Optional[str] = None
    counterAccountBankName: Optional[str] = None
    counterAccountName: Optional[str] = None
    counterAccountNumber: Optional[str] = None
    virtualAccountName: Optional[str] = None

class WebhookPayload(BaseModel):
    code: str
    desc: str
    success: bool
    signature: str
    data: WebhookData


class DonationBase(BaseModel):
    id: int
    campaign_id: int
    amount: Optional[Decimal]
    message: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


class DonationResponse(DonationBase):
    user_id: Optional[int] = None
    user_name: Optional[str] = None
    anonymous_name: Optional[str] = None
    transaction_id: Optional[str] = None
    bank_number: Optional[str] =  None
    bank_name: Optional[str] = None
    status: Optional[str]
    model_config = ConfigDict(from_attributes=True)


class DonationReq(BaseModel):
    campaign_id: int
    message: Optional[str] = None
    full_name: Optional[str]


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