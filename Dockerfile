# Sử dụng Python 3.11-slim làm base image tối ưu dung lượng
FROM python:3.11-slim

# Thiết lập các biến môi trường chuẩn của Python trong Docker
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive

# Thiết lập thư mục làm việc
WORKDIR /app

# Cài đặt các gói hệ thống cần thiết cho MySQL, PyTorch, OpenCV và Tesseract OCR
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    default-libmysqlclient-dev \
    pkg-config \
    tesseract-ocr \
    tesseract-ocr-vie \
    libgl1 \
    libglib2.0-0 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Cài đặt các thư viện Python
COPY requirements.txt /app/
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Sao chép toàn bộ mã nguồn dự án vào container
COPY . /app/

# Tạo các thư mục media và static nếu chưa tồn tại
RUN mkdir -p /app/media /app/static /app/logs

# Mở cổng 8000 cho Django Web Server
EXPOSE 8000

# Lệnh khởi chạy mặc định: Chạy migrations và start Django server
CMD ["sh", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]

