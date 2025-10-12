import logging
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession  # Quan trọng

from .models import User, UserProfile
from sqlalchemy.orm import selectinload, joinedload
from app.core.security import verify_password, get_password_hash
from .schemas import UserCreateReq, UserResponse, UpdateUserReq
from .mappers import UserMapper
from app.helpers.paging import PaginationParams, paginate, Page  # Giả sử paginate đã được sửa
from app.helpers.exception_handler import CustomException, ExceptionType



class UserService:
    def __init__(self):
        pass

    
    async def register(self, db: AsyncSession, data: UserCreateReq) -> UserResponse:
        query = select(User).options(selectinload(User.user_profile)).filter(User.email == data.email)
        result = await db.execute(query)
        exits_user = result.scalars().first()

        if exits_user:
            raise CustomException(error_type=ExceptionType.EMAIL_IS_TAKEN)
        profile = UserProfile(
            email=data.email
        )
        new_user = User(
            email=data.email,
            hash_password=get_password_hash(data.password),
            is_active=data.is_active,
            user_profile=profile,
            role=data.role
        )
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        result = await db.execute(
            select(User).options(selectinload(User.user_profile)).where(User.id == new_user.id)
        )
        loaded_user = result.scalar_one()
        logging.info(loaded_user.id)
        logging.info(loaded_user.user_profile.id)
        return UserMapper.to_user_response(loaded_user)

    async def get_my_profile(self, db: AsyncSession, user: User) -> UserResponse:
        query = select(User).options(selectinload(User.user_profile)).filter(User.id == user.id)
        result = await db.execute(query)
        loaded_user = result.scalars().first()
        if not loaded_user:
            raise CustomException(error_type=ExceptionType.USER_NOT_EXITS)
        return UserMapper.to_user_response(loaded_user)

    async def update_me(self, db: AsyncSession, user: User, data: UpdateUserReq) -> UserResponse:
        # user.email = user.email if data.email is None else data.email
        # user.role = user.role if data.role is None else data.role
        user.full_name = user.full_name if data.full_name is None else data.full_name
        user.logo = user.logo if data.logo is None and user.logo is not None else data.logo
        await db.commit()
        await db.refresh(user)
        return UserMapper.to_user_response(user)

    async def update(self, db: AsyncSession, user_id: int, data: UpdateUserReq) -> UserResponse:
        user = await db.get(User, user_id)
        if not user:
            raise CustomException(error_type=ExceptionType.USER_NOT_EXITS)

        user.email = user.email if data.email is None else data.email
        user.role = user.role if data.role is None else data.role
        user.full_name = user.full_name if data.full_name is None else data.full_name

        await db.commit()
        await db.refresh(user)
        return UserMapper.to_user_response(user)

    async def get_all_user(self, db: AsyncSession, params: PaginationParams):
        # 1. Tạo câu lệnh select()
        _query = select(User).options(
            joinedload(User.user_profile)
        )

        #

        mapper = UserMapper.to_user_response

        # 2. Gọi hàm paginate bất đồng bộ với await
        users = await paginate(
            db=db,
            model=User,
            query=_query,
            params=params,
            mapper=mapper
        )

        return users
