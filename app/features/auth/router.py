from fastapi import APIRouter, Depends, Response
from .schemas import Token, AuthReq
from .services import AuthService
from app.helpers.bases import DataResponse
from app.helpers.deps import get_current_user
from app.db.base import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.features.users.models import User
from app.core.config import settings

router = APIRouter()

def get_auth_service() -> AuthService:
    return AuthService()

@router.post('', response_model=DataResponse[Token])
async def authenticate(
    data: AuthReq, 
    response: Response,
    db: AsyncSession = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service)
):
    token = await auth_service.authenticate(db=db, data=data)
    return DataResponse(data=token)

@router.post('/refresh', response_model=DataResponse[Token])
async def refresh(
    token: str, 
    response: Response,
    db: AsyncSession = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service)
):
    new_token = await auth_service.refresh_token(db=db, token=token)
    return DataResponse(data=new_token)
