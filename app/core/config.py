from linebot import LineBotApi, WebhookHandler
from pydantic_settings import BaseSettings

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
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str = "your_host"
    POSTGRES_POST: str = "your_port"
    class Config:
        env_file = ".env"
        
postgress_settings = Postgres()