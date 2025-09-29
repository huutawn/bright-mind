import json
import logging
import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from minio import Minio
from minio.error import S3Error

from . import routers
from .helpers.bases import Base
from app.db.base import engine
from app.core.config import settings
from app.helpers.exception_handler import CustomException, http_exception_handler

logging.basicConfig(level=logging.INFO)


# ✅ Đưa logic MinIO vào một hàm riêng
def init_minio():
    try:
        minio_client = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=False
        )

        found = minio_client.bucket_exists(settings.MINIO_BUCKET)
        if not found:
            minio_client.make_bucket(settings.MINIO_BUCKET)
            # Thiết lập policy public-read cho bucket mới tạo
            policy = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {"AWS": ["*"]},
                        "Action": ["s3:GetObject"],
                        "Resource": [f"arn:aws:s3:::{settings.MINIO_BUCKET}/*"]
                    }
                ],
            }
            minio_client.set_bucket_policy(settings.MINIO_BUCKET, json.dumps(policy))
            logging.info(f"Bucket '{settings.MINIO_BUCKET}' đã được tạo và thiết lập public-read.")
        else:
            logging.info(f"Bucket '{settings.MINIO_BUCKET}' đã tồn tại.")

    except S3Error as exc:
        logging.error(f"Lỗi khi khởi tạo MinIO client: {exc}")
        raise


# ✅ Bỏ comment hàm này
# async def create_db_and_tables():
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.create_all)
#         logging.info("Các bảng trong database đã được tạo (nếu chưa tồn tại).")


def get_application() -> FastAPI:
    application = FastAPI(
        title=settings.PROJECT_NAME, docs_url="/docs", redoc_url='/re-docs',
        openapi_url=f"{settings.API_PREFIX}/openapi.json",
        description='''...'''
    )

    # ✅ Bỏ comment và gom các hàm khởi tạo vào đây
    @application.on_event("startup")
    async def on_startup():
        init_minio()
        # await create_db_and_tables()

    application.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    application.include_router(routers.router, prefix=settings.API_PREFIX)
    application.add_exception_handler(CustomException, http_exception_handler)

    return application


app = get_application()

if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)