from fastapi import APIRouter, Depends, Request

from app.core.payos_client import get_payos_client
from payos import PayOS
from .services import DonationService
from app.helpers.deps import get_current_user, get_current_user_optional
from app.helpers.bases import DataResponse
from app.helpers.paging import Page, PaginationParams
from app.domains.transaction.models import Donation
from app.domains.users.models import User
from app.helpers.login_manager import permission_required
from app.db.base import get_db
import json
import redis
from app.core.redis_client import get_redis_client
from app.domains.transaction.schemas import (
    DonationReq,
    DonationResponse,
    WithdrawalCreateReq,
    WithdrawalResponse,
    ProofCreateReq,
    ProofResponse,  
    ProofImageCreateReq,
    ProofImageResponse,
)
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()

def get_donation_service() -> DonationService:
    return DonationService()

@router.post('/donation', response_model=DataResponse[dict])
async def create_donation(data: DonationReq, db: AsyncSession = Depends(get_db),
                          donation_service: DonationService = Depends(get_donation_service),
                          user: User | None = Depends(get_current_user_optional),
                          payos_client: PayOS = Depends(get_payos_client)):
    res = await donation_service.create_donation(data, db, user, payos_client)
    return DataResponse(res)

@router.get('/donation', response_model=Page[DonationResponse])
async def get_all_donation(db: AsyncSession = Depends(get_db),
                          donation_service: DonationService = Depends(get_donation_service),
                          user: User = Depends(get_current_user_optional),
                          params: PaginationParams = Depends(),
                          redis_client: redis.Redis = Depends(get_redis_client)):
    cache_key = f"donation:page_{params.page}:size_{params.size}"
    cached_donations = redis_client.get(cache_key)
    if cached_donations:
        return Page[DonationResponse].model_validate(json.loads(cached_donations))
    res = await donation_service.get_all_donation(db, user, params)
    redis_client.set(cache_key, res.model_dump_json(), ex=600)
    return res

@router.get('/donation/campaign/{campaign_id}', response_model=Page[DonationResponse])
async def get_all_donation_by_campaign(campaign_id: int, db: AsyncSession = Depends(get_db),
                                       donation_service: DonationService = Depends(get_donation_service),
                                       params: PaginationParams = Depends(),
                                       redis_client: redis.Redis = Depends(get_redis_client)):
    cache_key = f"donation:campaign_{campaign_id}:page_{params.page}:size_{params.size}"
    cached_donations = redis_client.get(cache_key)
    if cached_donations:
        return Page[DonationResponse].model_validate(json.loads(cached_donations))

    res: Page[DonationResponse] = donation_service.get_all_donation_by_campaign(campaign_id, params, db)
    redis_client.set(cache_key, res.model_dump_json(), ex=600)
    return res
    
# Withdrawal routes
@router.post('/withdrawals', response_model=DataResponse[WithdrawalResponse])
async def create_withdrawal(data: WithdrawalCreateReq,
                            db: AsyncSession = Depends(get_db),
                            service: DonationService = Depends(get_donation_service)):
    res = await service.create_withdrawal(data, db)
    return DataResponse(res)


@router.get('/withdrawals/{status}', response_model=Page[WithdrawalResponse])
async def list_withdrawals(status: str, params: PaginationParams = Depends(),
                           db: AsyncSession = Depends(get_db),
                           service: DonationService = Depends(get_donation_service)):
    res = await service.get_all_withdrawals(status, params, db)
    return res


@router.get('/withdrawals/{withdrawal_id}', response_model=DataResponse[WithdrawalResponse])
async def get_withdrawal_detail(withdrawal_id: int,
                                db: AsyncSession = Depends(get_db),
                                service: DonationService = Depends(get_donation_service)):
    res = await service.get_withdrawal_detail(withdrawal_id, db)
    return DataResponse(res)


@router.delete('/withdrawals/{withdrawal_id}', response_model=DataResponse[bool])
async def delete_withdrawal(withdrawal_id: int,
                            db: AsyncSession = Depends(get_db),
                            service: DonationService = Depends(get_donation_service)):
    res = await service.delete_withdrawal(withdrawal_id, db)
    return DataResponse(res)


# Proof routes
@router.post('/proofs', response_model=DataResponse[ProofResponse])
async def create_proof(data: ProofCreateReq,
                       db: AsyncSession = Depends(get_db),
                       service: DonationService = Depends(get_donation_service)):
    res = await service.create_proof(data, db)
    return DataResponse(res)


@router.get('/withdrawals/{withdrawal_id}/proofs', response_model=Page[ProofResponse])
async def list_proofs_by_withdrawal(withdrawal_id: int,
                                    params: PaginationParams = Depends(),
                                    db: AsyncSession = Depends(get_db),
                                    service: DonationService = Depends(get_donation_service)):
    res = await service.get_proofs_by_withdrawal(withdrawal_id, params, db)
    return res


@router.get('/proofs/{proof_id}', response_model=DataResponse[ProofResponse])
async def get_proof_detail(proof_id: int,
                           db: AsyncSession = Depends(get_db),
                           service: DonationService = Depends(get_donation_service)):
    res = await service.get_proof_detail(proof_id, db)
    return DataResponse(res)


@router.delete('/proofs/{proof_id}', response_model=DataResponse[bool])
async def delete_proof(proof_id: int,
                       db: AsyncSession = Depends(get_db),
                       service: DonationService = Depends(get_donation_service)):
    res = await service.delete_proof(proof_id, db)
    return DataResponse(res)


# ProofImage routes
@router.post('/proof-images', response_model=DataResponse[ProofImageResponse])
async def add_proof_image(data: ProofImageCreateReq,
                          db: AsyncSession = Depends(get_db),
                          service: DonationService = Depends(get_donation_service)):
    res = await service.add_proof_image(data, db)
    return DataResponse(res)


@router.get('/proofs/{proof_id}/images', response_model=Page[ProofImageResponse])
async def list_proof_images(proof_id: int,
                            params: PaginationParams = Depends(),
                            db: AsyncSession = Depends(get_db),
                            service: DonationService = Depends(get_donation_service)):
    res = await service.get_proof_images_by_proof(proof_id, params, db)
    return res


@router.delete('/proof-images/{proof_image_id}', response_model=DataResponse[bool])
async def delete_proof_image(proof_image_id: int,
                             db: AsyncSession = Depends(get_db),
                             service: DonationService = Depends(get_donation_service)):
    res = await service.delete_proof_image(proof_image_id, db)
    return DataResponse(res)

@router.post('/webhooks', response_model=DataResponse[DonationResponse])
async def webhooks(data: Request,
                   db: AsyncSession = Depends(get_db),
                   service: DonationService = Depends(get_donation_service),
                   payos_client: PayOS = Depends(get_payos_client)):
    res = await service.transaction_handler(data, db, payos_client)
    return DataResponse(res)
