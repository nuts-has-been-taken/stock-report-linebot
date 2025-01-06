from linebot import LineBotApi, WebhookHandler
from pydantic_settings import BaseSettings
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

class Settings(BaseSettings):
    APP_NAME: str = "Line Stock Bot"
    DEBUG: bool = False
    
    # Line settings
    LINE_CHANNEL_ACCESS_TOKEN: str
    LINE_CHANNEL_SECRET: str
    
    class Config:
        env_file = ".env" 

settings = Settings()

class LineBot():
    def __init__(self):
        self.LINE_BOT_API = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)
        self.LINE_WEBHOOK = WebhookHandler(settings.LINE_CHANNEL_SECRET)

line_bot = LineBot()

class Postgres(BaseSettings):
    POSTGRES_URL: str
    ENGINE = create_engine(POSTGRES_URL)
    SESSION = sessionmaker(autocommit=False, autoflush=False, bind=ENGINE)
    class Config:
        env_file = ".env"
        
postgress_db = Postgres()