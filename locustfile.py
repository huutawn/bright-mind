import random
from locust import HttpUser, task, between
from faker import Faker

fake = Faker('vi_VN') # Sử dụng ngôn ngữ tiếng Việt để tạo dữ liệu giả

class BrightMindUser(HttpUser):
    """
    Kịch bản kiểm thử hiệu năng cho ứng dụng Bright Mind.
    Mô phỏng hành vi của người dùng:
    - Xem danh sách chiến dịch.
    - Xem chi tiết một chiến dịch.
    - Tạo một yêu cầu quyên góp (không hoàn thành thanh toán).
    - Xem danh sách các khoản quyên góp của một chiến dịch.
    - Xem danh sách các yêu cầu rút tiền.
    - Xem danh sách các bằng chứng minh bạch của một yêu cầu rút tiền.
    """
    wait_time = between(1, 5)  # Thời gian chờ ngẫu nhiên từ 1 đến 5 giây giữa các task
    host = "http://localhost:8000" # Địa chỉ host của ứng dụng

    def on_start(self):
        """
        Hàm này được chạy một lần cho mỗi người dùng ảo khi bắt đầu.
        Lấy danh sách các ID có sẵn để sử dụng trong các task khác.
        """
        self.campaign_ids = []
        self.withdrawal_ids = []
        
        try:
            # Lấy danh sách chiến dịch để có ID hợp lệ
            # Giả định API lấy danh sách campaigns có đường dẫn /api/campaigns
            with self.client.get("/api/campaigns/", name="/api/campaigns (get_ids)", catch_response=True) as response:
                if response.ok:
                    data = response.json().get('data', {})
                    items = data.get('items', [])
                    self.campaign_ids = [item['id'] for item in items if 'id' in item]
                    if not self.campaign_ids:
                        print("Cảnh báo: Không tìm thấy campaign ID nào để thực hiện các task khác.")
                else:
                    response.failure(f"Failed to get campaigns, status: {response.status_code}")

            # Lấy danh sách yêu cầu rút tiền để có ID hợp lệ
            # API này yêu cầu status, ta sẽ lấy các yêu cầu đang chờ xử lý 'pending'
            with self.client.get("/api/withdrawals/pending", name="/api/withdrawals/{status} (get_ids)", catch_response=True) as response:
                if response.ok:
                    # API này trả về cấu trúc Page, không có key 'data'
                    data = response.json().get('data', {})
                    items = data.get('items', [])
                    self.withdrawal_ids = [item['id'] for item in items if 'id' in item]
                    if not self.withdrawal_ids:
                        print("Không tìm thấy withdrawal ID nào.")
                else:
                    response.failure(f"Failed to get withdrawals, status: {response.status_code}")
        except Exception as e:
            print(f"Lỗi trong on_start: {e}")

    @task(5) # Task này có trọng số cao hơn, được chạy thường xuyên hơn
    def view_campaigns_and_details(self):
        """
        Task mô phỏng người dùng xem danh sách chiến dịch và sau đó xem chi tiết một chiến dịch ngẫu nhiên.
        """
        # 1. Xem danh sách tất cả chiến dịch (trang đầu tiên)
        self.client.get("/api/campaigns/?page=1&page_size=10", name="/api/campaigns")

        # 2. Nếu có campaign ID, xem chi tiết một campaign ngẫu nhiên
        if self.campaign_ids:
            campaign_id = random.choice(self.campaign_ids)
            self.client.get(f"/api/campaigns/{campaign_id}", name="/api/campaigns/{id}")

    @task(2)
    def create_donation(self):
        """
        Task mô phỏng người dùng tạo một yêu cầu quyên góp cho một chiến dịch ngẫu nhiên.
        """
        if self.campaign_ids:
            campaign_id = random.choice(self.campaign_ids)
            payload = {
                "campaign_id": campaign_id,
                "full_name": fake.name(),
                "message": fake.sentence(nb_words=10)
            }
            self.client.post("/api/donation", json=payload, name="/api/donation (create)")

    @task(3)
    def view_donations_and_proofs(self):
        """
        Task mô phỏng người dùng xem các danh sách liên quan đến minh bạch:
        - Danh sách quyên góp của một chiến dịch.
        - Danh sách yêu cầu rút tiền.
        - Danh sách bằng chứng của một yêu cầu rút tiền.
        """
        # 1. Xem danh sách quyên góp của một chiến dịch ngẫu nhiên
        if self.campaign_ids:
            campaign_id = random.choice(self.campaign_ids)
            self.client.get(
                f"/api/donation/campaign/{campaign_id}?page=1&page_size=10",
                name="/api/donation/campaign/{id}"
            )

        # 2. Xem danh sách các yêu cầu rút tiền (với status 'pending')
        self.client.get("/api/withdrawals/pending?page=1&page_size=10", name="/api/withdrawals/{status}")

        # 3. Xem danh sách bằng chứng của một yêu cầu rút tiền ngẫu nhiên
        if self.withdrawal_ids:
            withdrawal_id = random.choice(self.withdrawal_ids)
            # Sửa lại đường dẫn API cho chính xác
            self.client.get(
                f"/api/withdrawals/{withdrawal_id}/proofs?page=1&page_size=10",
                name="/api/withdrawals/{id}/proofs"
            )


# Để chạy kịch bản này:
# 1. Mở terminal ở thư mục gốc của dự án.
# 2. Chạy lệnh: locust -f locustfile.py
# 3. Mở trình duyệt và truy cập http://localhost:8089
# 4. Nhập số lượng người dùng ảo (Number of users) và tốc độ sinh người dùng (Spawn rate).
# 5. Bắt đầu kiểm thử.