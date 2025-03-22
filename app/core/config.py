from linebot import LineBotApi, WebhookHandler
from pydantic import model_validator
from pydantic_settings import BaseSettings
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from googleapiclient.discovery import build

class Settings(BaseSettings):
    APP_NAME: str = "Line Stock Bot"
    DEBUG: bool = False
    
    # Line settings
    LINE_CHANNEL_ACCESS_TOKEN: str
    LINE_CHANNEL_SECRET: str
    
    class Config:
        env_file = ".env"
        extra = "allow"

settings = Settings()

class LineBot():
    def __init__(self):
        self.LINE_BOT_API = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)
        self.LINE_WEBHOOK = WebhookHandler(settings.LINE_CHANNEL_SECRET)

line_bot = LineBot()

class GoogleAPI(BaseSettings):
    YOUTUBE_API_KEY: str
    
    @model_validator(mode="after")
    def init_youtube(self):
        self.YOUTUBE = build('youtube', 'v3', developerKey=self.YOUTUBE_API_KEY)
        return self
    
    class Config:
        env_file = ".env"
        extra = "allow"

google_api = GoogleAPI()

class Postgres(BaseSettings):
    POSTGRES_URL: str

    @model_validator(mode="after")
    def init_db(self):
        self.ENGINE = create_engine(self.POSTGRES_URL)
        self.SESSION = sessionmaker(autocommit=False, autoflush=False, bind=self.ENGINE)
        return self

    class Config:
        env_file = ".env"
        extra = "allow"
        
postgress_db = Postgres()