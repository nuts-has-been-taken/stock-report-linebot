from linebot import LineBotApi, WebhookHandler
from pydantic import model_validator
from pydantic_settings import BaseSettings
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from googleapiclient.discovery import build
from openai import OpenAI

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