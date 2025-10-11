from payos import PayOS
from app.core.config import settings 
# 1. Khởi tạo client MỘT LẦN DUY NHẤT
payos_client = PayOS(
    client_id=settings.PAYOS_CLIENT_ID,
    api_key=settings.PAYOS_API_KEY,
    checksum_key=settings.PAYOS_CHECKSUM_KEY
)

# 2. Tạo một dependency function
def get_payos_client() -> PayOS:
    """
    Dependency để cung cấp PayOS client cho các endpoint.
    """
    return payos_client