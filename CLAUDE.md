# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Taiwan stock market analysis LINE bot built with FastAPI. It provides automated market reports, institutional investor analysis, and real-time financial data through LINE messaging.

## Development Commands

### Environment Setup
```bash
# Install dependencies using Poetry
poetry install

# Run the application locally
poetry run uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Run with Docker
docker build -t stock-linebot .
docker-compose up -d
```

### Database
- PostgreSQL database with SQLAlchemy ORM
- Tables auto-created on application startup via `Base.metadata.create_all()`
- Configuration in `app/core/config.py`

### Scheduled Reports
- Install cron jobs: `bash cron_job_scripts/install_cron_jobs.sh`
- Daily reports at 15:05 (futures, major investors), 21:00 (margin), 11:00 (hao reports)

## Git Commit Guidelines

All commits must follow this emoji-based convention:

### Primary Emojis
- 🎉 `:tada:` - Initial commit or major milestone
- ✨ `:sparkles:` - New feature
- 🐛 `:bug:` - Bug fix
- 🚧 `:construction:` - Work in progress
- 🔧 `:wrench:` - Configuration changes
- 📦 `:package:` - Update dependencies
- 🎨 `:art:` - Code structure/format improvement
- ⚡ `:zap:` - Performance improvement
- 🔥 `:fire:` - Remove code/files
- 📝 `:memo:` - Documentation
- 🚀 `:rocket:` - Deployment

### Commit Format
```
<emoji> <type>: <description>

Examples:
✨ feat: add futures market analysis endpoint
🐛 fix: resolve LINE bot webhook timeout issue
🚧 wip: implement OpenAI integration for chat responses
🔧 config: update MinIO connection settings
```

## Architecture

### Clean Architecture Pattern
- **Router** (`app/router/`) - FastAPI route definitions
- **Controller** (`app/controller/`) - Request handling and orchestration  
- **Service** (`app/service/`) - Business logic implementation
- **Database** (`app/db/`) - Data access layer
- **Model** (`app/model/`) - SQLAlchemy models and MinIO setup
- **Schema** (`app/schema/`) - Pydantic models for validation

### Key Components
- **LINE Bot Integration**: Message handling, webhook processing
- **Report Generation**: Taiwan stock market analysis with matplotlib charts
- **MinIO Storage**: Image and file storage (replaced imgur)
- **OpenAI Integration**: Natural language processing for bot interactions
- **YouTube API**: Video content integration

## Configuration

### Environment Variables (.env)
- `LINE_CHANNEL_ACCESS_TOKEN` - LINE Bot API token
- `LINE_CHANNEL_SECRET` - LINE webhook verification
- `YOUTUBE_API_KEY` - YouTube Data API access
- `OPENAI_API_KEY` - OpenAI API for language processing
- `POSTGRES_*` - Database connection settings
- `MINIO_*` - Object storage configuration

### External APIs
- Taiwan Stock Exchange APIs for market data
- Yahoo Finance (`yfinance`) for additional stock data
- LINE Messaging API for bot functionality
- YouTube API for video content
- OpenAI API for chat processing

## Key Features

### Market Analysis Commands
- "法人" - Institutional investor reports
- "籌碼" - Stock chip analysis  
- "期貨" - Futures market data
- "保證金" - Margin trading analysis

### Automated Reports
- Daily institutional investor analysis
- Futures market summaries
- Margin trading statistics
- Chart generation with Chinese font support

## Development Notes

- Uses Poetry for dependency management
- FastAPI with async/await patterns
- SQLAlchemy 2.0+ with modern syntax
- Pydantic v2 for data validation
- Docker deployment with nginx proxy and SSL
- Chinese language support with Noto CJK fonts
- MinIO for persistent file storage

### Testing
- No test framework currently configured
- Manual testing via LINE bot interface
- API endpoints testable via FastAPI automatic docs at `/docs`