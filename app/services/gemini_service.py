import google.generativeai as genai
from app.core.config import settings
import logging

# Configure the API key
genai.configure(api_key=settings.GEMINI_API_KEY)

logger = logging.getLogger(__name__)

class GeminiService:
    def __init__(self, model_name: str = "gemini-1.5-flash"):
        self.model = genai.GenerativeModel(model_name)

    async def analyze_donation_proof(self, bill_image_data: bytes, charity_image_data: bytes) -> str:
        """
        Analyzes a bill image and a charity proof image to extract details.
        
        Args:
            bill_image_data: Raw bytes of the bill image.
            charity_image_data: Raw bytes of the charity proof image.
            
        Returns:
            JSON string containing the analysis result.
        """
        try:
            # Prepare the prompt
            prompt = """
            Bạn là một trợ lý AI chuyên phân tích các chứng từ tài chính và từ thiện.
            Hãy phân tích 2 bức ảnh sau:
            1. Ảnh hóa đơn (Bill): Trích xuất chi tiết các món đã mua, tổng tiền, ngày giờ, tên cửa hàng.
            2. Ảnh minh chứng từ thiện: Trích xuất tên tổ chức, số tiền quyên góp, nội dung chuyển khoản (nếu có).

            Hãy so sánh và kiểm tra xem số tiền hoặc nội dung có khớp nhau hoặc liên quan logic không (ví dụ: mua hàng xong quyên góp tiền lẻ, hoặc quyên góp theo chiến dịch).

            Trả về kết quả dưới dạng JSON thuần túy (không có markdown ```json ... ```) với cấu trúc sau:
            {
                "bill": {
                    "store_name": "...",
                    "items": [
                        {"name": "...", "quantity": 1, "price": 10000}
                    ],
                    "total_amount": 100000,
                    "date": "..."
                },
                "charity": {
                    "organization": "...",
                    "amount": 5000,
                    "message": "..."
                },
                "analysis": "Nhận xét về sự liên quan..."
            }
            """

            # Create content parts
            # Note: Gemini supports passing bytes directly via specific types or PIL images.
            # Here we convert bytes to the format expected by the SDK if needed, 
            # but the SDK often accepts a list of [prompt, image_blob].
            # For robustness, let's assume we pass the raw bytes wrapped in a dictionary specifying mime_type if possible,
            # or use a helper to convert to PIL Image if the SDK requires it.
            # The `google-generativeai` SDK supports passing a dict with 'mime_type' and 'data'.
            
            bill_part = {
                "mime_type": "image/jpeg", # Assuming JPEG for simplicity, or detect via magic numbers if needed
                "data": bill_image_data
            }
            charity_part = {
                "mime_type": "image/jpeg",
                "data": charity_image_data
            }

            response = self.model.generate_content([prompt, bill_part, charity_part])
            return response.text
        except Exception as e:
            logger.error(f"Error analyzing images with Gemini: {e}")
            return '{"error": "Failed to analyze images"}'

gemini_service = GeminiService()
