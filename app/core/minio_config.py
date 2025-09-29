from minio import Minio
from app.core.config import settings  # Giả sử bạn có file config

# 1. Khởi tạo client MỘT LẦN DUY NHẤT khi module này được import
minio_client = Minio(
    settings.MINIO_ENDPOINT,
    access_key=settings.MINIO_ACCESS_KEY,
    secret_key=settings.MINIO_SECRET_KEY,
    secure=False
)


# 2. Tạo một dependency function
def get_minio_client() -> Minio:
    """
    Dependency để cung cấp MinIO client cho các endpoint.
    """
    # Chỉ đơn giản là trả về client đã được khởi tạo
    return minio_client
