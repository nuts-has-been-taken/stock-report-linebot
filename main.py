from fastapi import FastAPI, Request
from linebot.models import MessageEvent, TextMessage, FollowEvent, JoinEvent
from linebot.exceptions import InvalidSignatureError
from contextlib import asynccontextmanager

from app.controller.line import handle_msg, handle_join, handle_follow
from app.core.config import line_bot, postgress_db
from app.model.line import Base

@asynccontextmanager
async def lifespan(app: FastAPI):
    # api start event
    Base.metadata.create_all(bind=postgress_db.ENGINE)
    yield
    # api shut down event

app = FastAPI(lifespan=lifespan)

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