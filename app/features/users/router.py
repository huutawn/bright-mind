from fastapi import APIRouter, Depends, Path
from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession  # ✅ Thêm import
import json
import redis
from app.core.redis_client import get_redis_client
from app.db.base import get_db  # ✅ Thêm import
from app.helpers.bases import DataResponse
from .schemas import UserCreateReq, UserResponse, UpdateUserReq
from .services import UserService
from .models import User
from app.helpers.deps import get_current_user, get_current_user_id
from app.helpers.paging import Page, PaginationParams
from app.helpers.login_manager import permission_required
import logging

router = APIRouter()


def get_user_service() -> UserService:
    return UserService()


require_admin_role = permission_required('admin')


@router.post('', response_model=DataResponse[UserResponse])
async def register(register_data: UserCreateReq,
                   db: AsyncSession = Depends(get_db),
                   user_service: UserService = Depends(get_user_service)
                   ):
    register_user = await user_service.register(db=db, data=register_data)
    return DataResponse(data=register_user)


@router.get('', response_model=DataResponse[UserResponse])
async def get_current_info(
        user: User = Depends(get_current_user),
        user_service: UserService = Depends(get_user_service),
        redis_client: redis.Redis = Depends(get_redis_client),
        db: AsyncSession = Depends(get_db)
):
    cache_key = f"user:{user.id}"
    cached_user = redis_client.get(cache_key)
    if cached_user:
        return DataResponse(data=UserResponse.model_validate(json.loads(cached_user)))
    response = await user_service.get_my_profile(db=db, user=user)
    redis_client.set(cache_key, response.model_dump_json(), ex=600)
    return DataResponse(data=response)


@router.put('', response_model=DataResponse[UserResponse])
# ✅ Chuyển sang async và nhận db session
async def update_me(update_data: UpdateUserReq,
                    user: User = Depends(get_current_user),
                    db: AsyncSession = Depends(get_db),
                    user_service: UserService = Depends(get_user_service),
                    redis_client: redis.Redis = Depends(get_redis_client)
                    ):
    cache_key = f"user:{user.id}"
    redis_client.delete(cache_key)
    user_updated = await user_service.update_me(db=db, user=user, data=update_data)
    return DataResponse(data=user_updated)


@router.put('/{user_id}', response_model=DataResponse[UserResponse])
# ✅ Chuyển sang async và nhận db session
async def update(data: UpdateUserReq,
                 user_id: int = Path(),
                 db: AsyncSession = Depends(get_db),
                 user_service: UserService = Depends(get_user_service),
                 redis_client: redis.Redis = Depends(get_redis_client)
                 ):
    cache_key = f"user:{user_id}"
    redis_client.delete(cache_key)
    user_updated = await user_service.update(db=db, id=user_id, data=data)
    return DataResponse(data=user_updated)


@router.get('/all', response_model=Page[UserResponse])
async def get_all(params: PaginationParams = Depends(),
                  db: AsyncSession = Depends(get_db),
                  current_admin: User = Depends(require_admin_role),
                  user_service: UserService = Depends(get_user_service),
                  redis_client: redis.Redis = Depends(get_redis_client)
                  ) -> Any:
    cache_key = f"users:page_{params.page}:size_{params.page_size}"
    cached_users = redis_client.get(cache_key)
    if cached_users:
        return Page[UserResponse].model_validate(json.loads(cached_users))

    users_page = await user_service.get_all_user(db=db, params=params)
    redis_client.set(cache_key, users_page.model_dump_json(), ex=600)
    return users_page
