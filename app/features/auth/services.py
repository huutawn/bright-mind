import logging
from datetime import datetime
import jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .schemas import Token, AuthReq
from app.features.users.models import User
from .models import InvalidateToken
from app.core.config import settings
from app.core.security import (
    verify_password,
    create_access_token,
    create_refresh_token
)
from app.helpers.exception_handler import CustomException, ExceptionType

from datetime import datetime, timezone
class AuthService:
    def __init__(self):
        pass

    # ✅ Chuyển sang async, nhận db, thêm self
    async def authenticate(self, db: AsyncSession, data: AuthReq) -> Token:
        query = select(User).filter(User.email == data.email)
        result = await db.execute(query)
        user: User | None = result.scalars().first()

        if not user:
            raise CustomException(error_type=ExceptionType.USER_NOT_EXITS)

        # verify_password là CPU-bound, không cần await
        if not verify_password(data.password, user.hash_password):
            raise CustomException(error_type=ExceptionType.WRONG_PASSWORD)
        user.last_login = datetime.now(timezone.utc)
        access_token = create_access_token(user=user)
        refresh_token = create_refresh_token(subject=user.id)
        await db.commit()
        return Token(access_token=access_token, refresh_token=refresh_token)

    # ✅ Chuyển sang async, nhận db
    async def refresh_token(self, db: AsyncSession, token: str) -> Token:
        try:
            # jwt.decode là CPU-bound, không cần await
            payload = jwt.decode(
                jwt=token,
                key=settings.SECRET_KEY,
                algorithms=[settings.SECURITY_ALGORITHM]
            )

            if payload.get('type') != 'refresh':
                raise CustomException(error_type=ExceptionType.INVALIDATE_TOKEN)

            user_id = int(payload.get('sub'))
            # ✅ Dùng await db.get() để lấy user theo ID
            user: User | None = await db.get(User, user_id)

            if not user:
                raise CustomException(error_type=ExceptionType.USER_NOT_EXITS)

            new_access_token = create_access_token(user=user)
            return Token(access_token=new_access_token, refresh_token=token)

        except (jwt.PyJWTError, CustomException) as e:
            logging.error(f"Failed to refresh token: {e}")
            raise CustomException(error_type=ExceptionType.INVALIDATE_TOKEN)

    # ✅ Chuyển sang async, nhận db
    async def log_out(self, db: AsyncSession, token: str):
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.SECURITY_ALGORITHM])

        jti = payload.get('jti')
        exp = payload.get('exp')

        if not jti:
            raise CustomException(error_type=ExceptionType.INVALIDATE_TOKEN, message="Token does not have JTI")

        invalidated_token = InvalidateToken(jti=jti, exp=datetime.fromtimestamp(exp))
        db.add(invalidated_token)
        # ✅ Dùng await cho commit
        await db.commit()
        return 'success'