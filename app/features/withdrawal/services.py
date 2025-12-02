from .schemas import (
    WithdrawalResponse,
    WithdrawalCreateReq,
    ProofCreateReq,
    ProofResponse,
    ProofImageResponse,
    ProofImageCreateReq
)
from .models import(
    Withdrawal,
    Proof, ProofImage
)
from sqlalchemy.ext.asyncio import AsyncSession
from app.helpers.exception_handler import CustomException, ExceptionType
from ..campaigns.models import Campaign
from ..users.models import User
from datetime import datetime
from fastapi import HTTPException, Request
from sqlalchemy.orm import selectinload
from sqlalchemy import select
from app.helpers.paging import paginate, PaginationParams
from .schemas import (
    WithdrawalResponse,
    WithdrawalCreateReq,
    ProofCreateReq,
    ProofResponse,
    ProofImageResponse,
    ProofImageCreateReq
)
from .models import(
    Withdrawal,
    Proof, ProofImage
)
from sqlalchemy.ext.asyncio import AsyncSession
from app.helpers.exception_handler import CustomException, ExceptionType
from ..campaigns.models import Campaign
from ..users.models import User
from datetime import datetime
from fastapi import HTTPException, Request
from sqlalchemy.orm import selectinload
from sqlalchemy import select
from app.helpers.paging import paginate, PaginationParams
from decimal import Decimal
from typing import Optional
from .interface import ITransactionService
from app.helpers.enums import WithdrawalStatus
from .mappers import WithdrawalMapper

class WithdrawalService:
    async def create_withdrawal(self,
                                data: WithdrawalCreateReq,
                                db: AsyncSession) -> WithdrawalResponse:
        campaign: Campaign | None = await db.get(Campaign, data.campaign_id)
        if not campaign:
            raise CustomException(error_type=ExceptionType.CAMPAIGN_NOT_FOUND)
        # Check latest withdrawal status in this campaign (lấy tối đa 2 giao dịch gần nhất)
        last_withdrawal_result = await db.execute(
            select(Withdrawal)
            .filter(Withdrawal.campaign_id == campaign.id)
            .order_by(Withdrawal.created_at.desc())
            .limit(2)
        )
        last_withdrawals: list[Withdrawal] = list(last_withdrawal_result.scalars().all())
        
        if last_withdrawals:
            has_pending_withdrawal = any(
                w.status in [WithdrawalStatus.PENDING.value, WithdrawalStatus.WAITING.value] 
                for w in last_withdrawals
            )
            has_quickly_withdrawal = any(
                w.type == 'quickly' and w.status in [WithdrawalStatus.PENDING.value, WithdrawalStatus.WAITING.value]
                for w in last_withdrawals
            )
            
            if has_pending_withdrawal and data.type == 'normal':
                raise CustomException(error_type=ExceptionType.FAIL_TO_GET, custom_message='Không thể tạo withdrawal bình thường khi có giao dịch đang chờ xử lý')
            if has_quickly_withdrawal and data.type == 'quickly':
                raise CustomException(error_type=ExceptionType.FAIL_TO_GET, custom_message='Bạn đã tạo giao dịch khẩn cấp trước đó rồi')
        if data.type == 'quickly':
            if data.amount > campaign.current_amount*(Decimal(0.3)):
                raise CustomException(error_type=ExceptionType.FAIL_TO_GET, custom_message='số tiền bạn muốn rút khẩn cấp vượt quá 30% số tiền đã đóng góp')
            else:
                campaign.quickly_used = True
            
        withdrawal = Withdrawal(
            campaign_id=campaign.id,
            amount=data.amount,
            type=data.type,
            reason=data.reason,
        )
        db.add(withdrawal)
        await db.commit()
        await db.refresh(withdrawal)
        return WithdrawalMapper.to_withdrawal_response(withdrawal)

    async def get_all_withdrawals(self, status: str, params: PaginationParams, db: AsyncSession):
        query = select(Withdrawal).options(
        )
        if status:
            query = query.filter(Withdrawal.status == status)
        withdrawals = await paginate(db=db, model=Withdrawal,
                                     query=query, params=params, mapper=WithdrawalMapper.to_withdrawal_response)
        return withdrawals

    async def get_withdrawal_detail(self, withdrawal_id: int, db: AsyncSession) -> WithdrawalResponse:
        withdrawal: Withdrawal | None = await db.get(Withdrawal, withdrawal_id)
        if not withdrawal:
            raise CustomException(error_type=ExceptionType.FAIL_TO_GET, custom_message='Withdrawal not found')
        return WithdrawalMapper.to_withdrawal_response(withdrawal)

    async def delete_withdrawal(self, withdrawal_id: int, db: AsyncSession) -> bool:
        withdrawal: Withdrawal | None = await db.get(Withdrawal, withdrawal_id)
        if not withdrawal:
            raise CustomException(error_type=ExceptionType.FAIL_TO_GET, custom_message='Withdrawal not found')
        await db.delete(withdrawal)
        await db.commit()
        return True

    # Proof CRUD
    async def create_proof(self,
                           data: ProofCreateReq,
                           db: AsyncSession) -> ProofResponse:
        withdrawal: Withdrawal | None = await db.get(Withdrawal, data.withdrawal_id)
        if not withdrawal:
            raise CustomException(error_type=ExceptionType.FAIL_TO_GET, custom_message='Withdrawal not found')
        proof = Proof(
            withdrawal_id=withdrawal.id,
            description=data.description,
        )
        db.add(proof)
        await db.commit()
        await db.refresh(proof)
        return WithdrawalMapper.to_proof_response(proof)

    async def get_proofs_by_withdrawal(self, withdrawal_id: int, params: PaginationParams, db: AsyncSession):
        query = select(Proof).options(
        ).filter(Proof.withdrawal_id == withdrawal_id)
        proofs = await paginate(db=db, model=Proof,
                                query=query, params=params)
        return proofs

    async def get_proof_detail(self, proof_id: int, db: AsyncSession) -> ProofResponse:
        proof: Proof | None = await db.get(Proof, proof_id)
        if not proof:
            raise CustomException(error_type=ExceptionType.FAIL_TO_GET, custom_message='Proof not found')
        return WithdrawalMapper.to_proof_response(proof)

    async def delete_proof(self, proof_id: int, db: AsyncSession) -> bool:
        proof: Proof | None = await db.get(Proof, proof_id)
        if not proof:
            raise CustomException(error_type=ExceptionType.FAIL_TO_GET, custom_message='Proof not found')
        await db.delete(proof)
        await db.commit()
        return True

    # ProofImage CRUD
    async def add_proof_image(self, data: ProofImageCreateReq, db: AsyncSession) -> ProofImageResponse:
        proof: Proof | None = await db.get(Proof, data.proof_id)
        if not proof:
            raise CustomException(error_type=ExceptionType.FAIL_TO_GET, custom_message='Proof not found')
        proof_image = ProofImage(
            proof_id=proof.id,
            image_url=data.image_url,
        )
        db.add(proof_image)
        await db.commit()
        await db.refresh(proof_image)
        return WithdrawalMapper.to_proof_image_response(proof_image)

    async def get_proof_images_by_proof(self, proof_id: int, params: PaginationParams, db: AsyncSession):
        query = select(ProofImage).options(
        ).filter(ProofImage.proof_id == proof_id)
        images = await paginate(db=db, model=ProofImage,
                                query=query, params=params)
        return images

    async def delete_proof_image(self, proof_image_id: int, db: AsyncSession) -> bool:
        proof_image: ProofImage | None = await db.get(ProofImage, proof_image_id)
        if not proof_image:
            raise CustomException(error_type=ExceptionType.FAIL_TO_GET, custom_message='ProofImage not found')
        await db.delete(proof_image)
        await db.commit()
        return True