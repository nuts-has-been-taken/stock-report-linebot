from fastapi import FastAPI, Request
from linebot.models import MessageEvent, TextMessage, FollowEvent, JoinEvent
from linebot.exceptions import InvalidSignatureError
from contextlib import asynccontextmanager

from app.controller.line import handle_msg, handle_join, handle_follow
from app.core.config import line_bot, postgress_db
from app.model.postgresql import Base
from app.model.minio import ensure_buckets_exist

from app.router.youtube import router as youtube_router
from app.router.line import router as line_router
from app.router.report import router as report_router
from app.router.minio import router as minio_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # api start event
    
    # Create database table
    Base.metadata.create_all(bind=postgress_db.ENGINE)
    # Ensure MinIO buckets exist
    ensure_buckets_exist()
    
    yield
    # api shut down event

app = FastAPI(lifespan=lifespan)

# Add Routers
app.include_router(youtube_router, prefix="/youtube", tags=["YouTube"])
app.include_router(line_router, prefix="/line", tags=["Line"])
app.include_router(report_router, prefix="/report", tags=["Report"])
app.include_router(minio_router, prefix="/img", tags=["MinIO"])

# Line webhook
handler = line_bot.LINE_WEBHOOK

@app.get("/")
def read_root():
    return {"message": "Stock line bot service is running!"}

@app.post("/callback")
async def callback(request: Request):
    signature = request.headers['X-Line-Signature']
    body = await request.body()
    try:
        handler.handle(body.decode('utf-8'), signature)
    except InvalidSignatureError:
        return "Invalid signature", 400
    return "OK"

@handler.add(MessageEvent, message=TextMessage)
def recieve_msg(event:MessageEvent):
    handle_msg(event=event)
    
@handler.add(JoinEvent)
def new_join(event:JoinEvent):
    handle_join(event=event)

@handler.add(FollowEvent)
def new_follow(event:FollowEvent):
    handle_follow(event=event)