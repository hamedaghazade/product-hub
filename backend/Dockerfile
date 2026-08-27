FROM python:3.11-slim

# تنظیم متغیرهای محیطی پایتون
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive

WORKDIR /app

# نصب ابزارهای سیستمی و کتابخانه‌های مورد نیاز WeasyPrint و Pillow
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libharfbuzz0b \
    libjpeg-dev \
    libopenjp2-7-dev \
    fonts-dejavu \
    fonts-freefont-ttf \
    curl \
    && rm -rf /var/lib/apt/lists/*

# کپی فونت فارسی Vazirmatn در سیستم
RUN mkdir -p /usr/share/fonts/truetype/vazirmatn
COPY assets/fonts/ /usr/share/fonts/truetype/vazirmatn/
RUN fc-cache -f -v

# نصب نیازمندی‌های پایتون
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# کپی کدهای برنامه
COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]