FROM python:3.13-slim

# 設定工作目錄
WORKDIR /linebot

# 安裝系統依賴，包含 PostgreSQL 開發庫和編譯工具
RUN apt-get update && apt-get install -y \
    libpq-dev gcc python3-dev&& \
    apt-get install -y fonts-noto-cjk &&\
    rm -rf /var/lib/apt/lists/*

# 避免建立虛擬環境
ENV POETRY_VIRTUALENVS_CREATE=false

# 安裝 Poetry
RUN pip install poetry

COPY pyproject.toml poetry.lock /linebot/

COPY .env /linebot/

# 安裝 Python 依賴
RUN poetry install --no-root