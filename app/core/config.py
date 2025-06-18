from linebot import LineBotApi, WebhookHandler
from pydantic import model_validator
from pydantic_settings import BaseSettings
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from googleapiclient.discovery import build
from openai import OpenAI
from minio import Minio

class CommonConfig(BaseSettings):
    class Config:
        env_file = ".env"
        extra = "allow"

class LineBot(CommonConfig):
    LINE_CHANNEL_ACCESS_TOKEN: str
    LINE_CHANNEL_SECRET: str
    
    @model_validator(mode="after")
    def init_line(self):
        self.LINE_BOT_API = LineBotApi(self.LINE_CHANNEL_ACCESS_TOKEN)
        self.LINE_WEBHOOK = WebhookHandler(self.LINE_CHANNEL_SECRET)
        return self

line_bot = LineBot()

class GoogleAPI(CommonConfig):
    YOUTUBE_API_KEY: str
    
    @model_validator(mode="after")
    def init_youtube(self):
        self.YOUTUBE = build('youtube', 'v3', developerKey=self.YOUTUBE_API_KEY)
        return self

google_api = GoogleAPI()

class OpenAIClient(CommonConfig):
    OPENAI_API_KEY: str
    AUDIO_MODE: bool = False
    TRANS_FIRST: bool = False
    
    @model_validator(mode="after")
    def init_openai(self):
        self.client = OpenAI(api_key=self.OPENAI_API_KEY)
        return self
        
openai_client = OpenAIClient()

class Postgres(CommonConfig):
    POSTGRES_URL: str

    @model_validator(mode="after")
    def init_db(self):
        self.ENGINE = create_engine(self.POSTGRES_URL)
        self.SESSION = sessionmaker(autocommit=False, autoflush=False, bind=self.ENGINE)
        return self

postgress_db = Postgres()

class MinIOClient(CommonConfig):
    MINIO_ENDPOINT: str = "localhost"
    MINIO_PORT: int = 9000
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_USE_SSL: bool = False

    @model_validator(mode="after")
    def init_minio(self):
        self.client = Minio(
            endpoint=self.MINIO_ENDPOINT,
            access_key=self.MINIO_ACCESS_KEY,
            secret_key=self.MINIO_SECRET_KEY,
            secure=self.MINIO_USE_SSL
        )
        return self

minio_client = MinIOClient()