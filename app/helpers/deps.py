from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer
import jwt
from pydantic import ValidationError
from app.core.config import settings
from typing import Optional
from app.db.base import get_db
from sqlalchemy import select
from ..features.users.models import User
from ..features.auth.models import InvalidateToken
from ..features.users.schemas import TokenPayload
from sqlalchemy.ext.asyncio import AsyncSession
import logging

reusable_oauth2 = HTTPBearer(scheme_name='Authorization', auto_error=False)

async def get_current_user(db: AsyncSession = Depends(get_db), request: Request = None) -> User:
    """
    Decode JWT token from Authorization header or http-only cookie to get user_id,
    then return User info from DB query.
    """
    token = None
    auth_header = await reusable_oauth2(request)
    if auth_header:
        token = auth_header.credentials

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )

    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY,
            algorithms=[settings.SECURITY_ALGORITHM]
        )
        token_data = TokenPayload(sub=payload.get('sub'), jti=payload.get('jti'), type=payload.get('type'))

        if token_data.type == 'refresh':
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Refresh token cannot be used for authentication'
            )

        token_jti = token_data.jti
        if not token_jti:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='Could not get JTI from token'
            )

        query_is_invalid = select(InvalidateToken).filter(InvalidateToken.jti == token_data.jti)
        result = await db.execute(query_is_invalid)
        is_invalid = result.scalars().first()
        if is_invalid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Token has been invalidated'
            )

    except (jwt.PyJWTError, ValidationError) as e:
        logging.error(f"Token validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )

    user = await db.get(User, int(token_data.sub))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user

async def get_current_user_optional(db: AsyncSession = Depends(get_db), request: Request = None) -> Optional[User]:
    try:
        return await get_current_user(db, request)
    except HTTPException:
        return None
async def get_current_user_id(db: AsyncSession = Depends(get_db),
                           http_authorization_credentials=Depends(reusable_oauth2)) -> int:
    """
    Decode JWT token to get user_id => return User info from DB query
    """
    logging.warning('token')
    try:
        payload = jwt.decode(
            http_authorization_credentials.credentials, settings.SECRET_KEY,
            algorithms=[settings.SECURITY_ALGORITHM]
        )
        token_data = TokenPayload(sub=payload.get('sub'), jti=payload.get('jti'), type=payload.get('type'))
        if token_data.type == 'refresh':
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='user is not authenticated'

            )
        token_jti = token_data.jti
        logging.info(token_jti)
        if not token_jti:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='could not get jti'
            )
        query_is_valid = select(InvalidateToken).filter(InvalidateToken.jti == token_data.jti)
        result = await db.execute(query_is_valid)
        is_valid = result.scalars().first()
        logging.info(is_valid)
        if is_valid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='user is not authenticated'
            )
        int_token = int(token_data.sub)
    except (jwt.PyJWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Could not validate credentials",
        )
    return int(token_data.sub)


