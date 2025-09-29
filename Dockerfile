# =====================================================================
# STAGE 1: Build Stage
#
# Mục đích của stage này là cài đặt tất cả dependencies.
# Stage này sẽ được loại bỏ sau khi build xong, giữ cho image cuối cùng gọn nhẹ.
# =====================================================================
# Sử dụng phiên bản Python mới nhất và base image "slim" để giảm dung lượng
FROM python:3.12-slim as builder

# Đặt biến môi trường để tối ưu
# PYTHONDONTWRITEBYTECODE=1: Ngăn Python tạo file .pyc
# PYTHONUNBUFFERED=1: Đảm bảo log được ghi ra ngay lập tức
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Tạo một virtual environment để quản lý dependencies một cách cô lập
# Điều này giúp dễ dàng copy toàn bộ dependencies sang stage sau
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /app

# Chỉ copy file requirements.txt trước
# Tận dụng Docker layer caching: Bước này chỉ chạy lại khi requirements.txt thay đổi
COPY requirements.txt .

# Cài đặt dependencies vào virtual environment
# --no-cache-dir: Không lưu cache của pip để giảm dung lượng
# --upgrade pip: Luôn sử dụng phiên bản pip mới nhất
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt


# =====================================================================
# STAGE 2: Final/Production Stage
#
# Stage này sẽ chứa image cuối cùng để chạy ứng dụng.
# Nó chỉ lấy những thứ cần thiết từ "builder" stage.
# =====================================================================
FROM python:3.12-slim

WORKDIR /app

# Copy virtual environment đã được cài đặt từ builder stage
COPY --from=builder /opt/venv /opt/venv

# Copy toàn bộ code của ứng dụng
COPY . .

# Tạo một user và group riêng để chạy ứng dụng (best practice về bảo mật)
# Tránh chạy ứng dụng với quyền root
RUN groupadd -r app_group && useradd --no-log-init -r -g app_group app_user
RUN chown -R app_user:app_group /app

# Kích hoạt virtual environment cho các lệnh sau
ENV PATH="/opt/venv/bin:$PATH"

# Chuyển sang user không phải root
USER app_user

# Expose port mà ứng dụng sẽ chạy
EXPOSE 8000

# Lệnh để chạy ứng dụng khi container khởi động
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
