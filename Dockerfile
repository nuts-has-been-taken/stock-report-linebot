FROM python:3.11-slim

# 設定工作目錄
WORKDIR /linebot

# 安裝 Poetry
RUN pip install poetry

COPY pyproject.toml poetry.lock /linebot/

# 安裝 Python 依賴
RUN poetry install --no-dev