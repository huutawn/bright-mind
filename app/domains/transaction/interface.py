from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Optional
from fastapi import Request 
from sqlalchemy.ext.asyncio import AsyncSession

from .schemas import  DonationReq, WithdrawalCreateReq, WithdrawalResponse, ProofCreateReq, ProofResponse, ProofImageCreateReq, ProofImageResponse
from .models import Withdrawal, Proof, ProofImage
from app.helpers.paging import PaginationParams
from ..users.models import User


class ITransactionService(ABC):
    @abstractmethod
    async def transaction_handler(self, data: Request, db: AsyncSession):
        pass

    @abstractmethod
    async def create_donation(self, data: DonationReq, db: AsyncSession, user: User):
        pass

    @abstractmethod
    async def get_all_donation(self, db: AsyncSession, user: User | None = None):
        pass

    @abstractmethod
    async def get_all_donation_by_campaign(self, campaign_id: int, params: PaginationParams, db: AsyncSession):
        pass

    @abstractmethod
    async def get_all_donation_by_user(self, user_id: int, params: PaginationParams, db: AsyncSession):
        pass

    # Withdrawal
    @abstractmethod
    async def create_withdrawal(self, data: WithdrawalCreateReq, db: AsyncSession) -> WithdrawalResponse:
        pass

    @abstractmethod
    async def get_all_withdrawals(self, params: PaginationParams, db: AsyncSession):
        pass

    @abstractmethod
    async def get_withdrawal_detail(self, withdrawal_id: int, db: AsyncSession) -> WithdrawalResponse:
        pass

    @abstractmethod
    async def delete_withdrawal(self, withdrawal_id: int, db: AsyncSession) -> bool:
        pass

    # Proof
    @abstractmethod
    async def create_proof(self, data: ProofCreateReq, db: AsyncSession) -> ProofResponse:
        pass

    @abstractmethod
    async def get_proofs_by_withdrawal(self, withdrawal_id: int, params: PaginationParams, db: AsyncSession):
        pass

    @abstractmethod
    async def get_proof_detail(self, proof_id: int, db: AsyncSession) -> ProofResponse:
        pass

    @abstractmethod
    async def delete_proof(self, proof_id: int, db: AsyncSession) -> bool:
        pass

    # ProofImage
    @abstractmethod
    async def add_proof_image(self, data: ProofImageCreateReq, db: AsyncSession) -> ProofImageResponse:
        pass

    @abstractmethod
    async def get_proof_images_by_proof(self, proof_id: int, params: PaginationParams, db: AsyncSession):
        pass

    @abstractmethod
    async def delete_proof_image(self, proof_image_id: int, db: AsyncSession) -> bool:
        pass


