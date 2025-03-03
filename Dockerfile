FROM python:3.11-slim

# 設定工作目錄
WORKDIR /linebot

# 安裝系統依賴，包含 PostgreSQL 開發庫和編譯工具
RUN apt-get update && apt-get install -y \
    libpq-dev gcc && \
    rm -rf /var/lib/apt/lists/*
    
# 安裝 Poetry
RUN pip install poetry

COPY pyproject.toml poetry.lock /linebot/

COPY .env /linebot/

# 安裝 Python 依賴
RUN poetry install --no-root