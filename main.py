from linebot import LineBotApi
from linebot.models import TextSendMessage
from dotenv import load_dotenv
import os

load_dotenv()

LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)

USER_ID = '用戶的_LINE_USER_ID'

def push_message(user_id, message):
    try:
        line_bot_api.push_message(user_id, TextSendMessage(text=message))
        print("訊息已發送")
    except Exception as e:
        print(f"發送失敗: {e}")

if __name__ == "__main__":
    message = "這是一則單向推播訊息！"
    push_message(USER_ID, message)
