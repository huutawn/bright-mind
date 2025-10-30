from fastapi import APIRouter

from .features.users import router as user_router
from .features.auth import router as auth_router
from .features.files import routers as file_router
from .features.campaigns import routers as campaign_router
from .features.transaction import routers as transaction_router
router = APIRouter()

router.include_router(user_router.router, tags=["users"], prefix="/users")
router.include_router(auth_router.router, tags=['AUTH'], prefix="/auth")
router.include_router(file_router.router, tags=['files'],prefix='/upload')
router.include_router(campaign_router.router, tags=['Campaign'], prefix='/campaign')
router.include_router(transaction_router.router, tags=['Transaction'], prefix='/transaction')