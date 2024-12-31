from fastapi import FastAPI, Request
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, FollowEvent
from linebot.exceptions import InvalidSignatureError
import os

app = FastAPI()

LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

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

@handler.add(MessageEvent)
def handle_msg(event:MessageEvent):
    if event.source.type == "user":
        user_id = event.source.user_id
        print(f"用戶 ID: {user_id}")
    elif event.source.type == "group":
        group_id = event.source.group_id
        print(f"群組 ID: {group_id}")
    elif event.source.type == "room":
        room_id = event.source.room_id
        print(f"聊天室 ID: {room_id}")