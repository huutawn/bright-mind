from .schemas import (
    DonationReq,
    DonationResponse,
)
from .models import Donation, TransactionError
from app.helpers.exception_handler import CustomException, ExceptionType
from sqlalchemy.ext.asyncio import AsyncSession
from ..campaigns.models import Campaign
from ..users.models import User
from .mappers import TransactionMapper
from datetime import datetime
from fastapi import HTTPException, Request
from payos import PayOS, PaymentData
from payos.type import WebhookData
import re
from sqlalchemy.orm import selectinload
from sqlalchemy import select
from app.helpers.paging import paginate, PaginationParams
from decimal import Decimal
from typing import Optional
from .interface import ITransactionService

class DonationService(ITransactionService):
    def __init__(self):
        pass

    async def transaction_handler(self, data: Request, db: AsyncSession, payos_client: PayOS):
        webhook_body = await data.json()

        try:
            verified_data: WebhookData = payos_client.verifyPaymentWebhookData(webhook_body) # Có thể raise Exception

            original_description = verified_data['description']
            amount = verified_data['amount']
            bank_number = verified_data['counterAccountNumber']
            bank_name = verified_data['counterAccountName']

            # 1. Trích xuất campaign_id từ giữa hai chuỗi 'brm'
            campaign_id_match = re.search(r'brm(\d+)brm', original_description)

            # 2. Trích xuất new_code là chuỗi bắt đầu bằng 'TSS'
            new_code_match = re.search(r'(TSS.*)', original_description)

            # 3. Kiểm tra xem cả hai thông tin có hợp lệ không
            if not campaign_id_match or not new_code_match:
                raise CustomException(error_type=ExceptionType.FAIL_TO_GET, custom_message=f"Invalid transaction code format: {original_description}")

            campaign_id = campaign_id_match.group(1)
            new_code = new_code_match.group(1)

            res_donate = await db.execute(
                select(Donation).filter(Donation.code == new_code)
            )
            donation: Donation | None = res_donate.scalar_one_or_none()
            if not donation:
                transaction_err = TransactionError(
                    bank_name=bank_name,
                    bank_number=bank_number,
                    amount=amount,
                    content=original_description,
                    status='pending'
                )
                db.add(transaction_err)
                await db.commit()
                raise CustomException(error_type=ExceptionType.FAIL_TO_GET, custom_message='Donation not found')
            campaign = await db.get(Campaign, campaign_id, with_for_update=True)
            donation.amount = Decimal(amount)
            donation.bank_number = bank_number
            donation.bank_name = bank_name
            donation.status = 'success'
            campaign.current_amount += Decimal(amount)
            await db.commit()
            await db.refresh(donation)
            await db.refresh(campaign)
            return TransactionMapper.to_donation_response(donation)
        except Exception as e:
            # Bắt các lỗi chung khác (lỗi database, logic,...)
            raise CustomException(error_type=ExceptionType.FAIL_TO_GET, custom_message=str(e))



             

        

    async def create_donation(self, data: DonationReq, db: AsyncSession, user: User| None, payos_client: PayOS)-> dict:
        campaign: Campaign | None = await db.get(Campaign, data.campaign_id)
        if not campaign:
            raise CustomException(error_type=ExceptionType.CAMPAIGN_NOT_FOUND)
        code = f'TSSSbrm{campaign.id}brm{int(datetime.now().timestamp())}'
        donation: Donation = Donation(
            campaign_id=campaign.id,
            code=code,
            message=data.message,
            user_id=user.id if user else None,
            anonymous_name=data.full_name if not user else None,
            user_name=data.full_name if user else None,
            transaction_id=code,
            bank_number='',
            bank_name='',
            amount=Decimal(0), 
        )
        db.add(donation)
        await db.commit()
        await db.refresh(donation)
        payment_data = PaymentData(amount=100000,orderCode=donation.id, description=code, returnUrl=f"https://your-frontend.com/donation/success/{donation.id}",
                                   cancelUrl=f"https://your-frontend.com/donation/failed/{donation.id}")
    
        try:
            payment_link_info = payos_client.createPaymentLink(paymentData=payment_data)
            return payment_link_info
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def get_all_donation(self, db: AsyncSession, user: User | None = None, params: PaginationParams = None):
        query = select(Donation).options(
        )
        mapper = TransactionMapper.to_donation_response
        donations = await paginate(db=db, model=Donation,
                                   query=query, params=params, mapper=mapper)
        return donations

    async def get_all_donation_by_campaign(self, campaign_id: int, params: PaginationParams, db: AsyncSession):
        query = select(Donation).options(
        ).filter(Donation.campaign_id == campaign_id)
        mapper = TransactionMapper.to_donation_response
        donations = await paginate(db=db, model=Donation,
                                   query=query,params=params,mapper=mapper)
        return donations
    

    

    async def get_all_donation_by_user(self, user_id: int, params: PaginationParams, db: AsyncSession):
        query = select(Donation).options(
        ).filter(Donation.user_id == user_id)
        mapper = TransactionMapper.to_donation_response
        donations = await paginate(db=db, model=Donation,
                                   query=query,params=params,mapper=mapper)
        return donations
    
    
