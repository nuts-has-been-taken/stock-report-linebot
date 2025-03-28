from linebot.models import MessageEvent, JoinEvent, FollowEvent

from app.service.line import fetch_daily_report, hao_report
from app.util.line import get_event_id, get_reply_token, push_message, reply_message
from logger import logger

def handle_msg(event:MessageEvent):
    """Handle message event from Line bot

    Args:
        event (MessageEvent): Message event from Line bot
    """
    
    event_type, event_id = get_event_id(event)
    reply_token = get_reply_token(event)
    print(f"Event_type: {event_type}, Event_id: {event_id}, Text: {event.message.text}")
    # 日報
    if event.message.text in ["法人", "籌碼", "期貨"]:
        # reply_message(reply_token=reply_token, message="請稍等，正在查詢中...")
        try:
            fetch_daily_report(event_id=event_id, report_type=event.message.text)
            return
        except Exception as e:
            logger.error(f"Error: {e}")
            push_message(to=event_id, message="查詢失敗，請稍後再試")
            return
    elif event.message.text=="hao":
        try:
            hao_report(event_id=event_id, cron_mode=False)
            return
        except Exception as e:
            logger.error(f"Error: {e}")
            push_message(to=event_id, message="查詢失敗，請稍後再試")
            return
    elif event.message.text in ["幫助", "help", "Help", "-h", "-H"]:
        push_message(to=event_id, message=help_message)
    else:
        # 聊天室或群組一般聊天不回覆
        if event.source.type == "user":
            reply_message(reply_token=reply_token, message=else_message)

def get_daily_report(event_id: str, report_type: str, data_number: int = 20):
    try:
        fetch_daily_report(event_id, report_type, data_number)
        return {"result": "success"}
    except Exception as e:
        return {"result": "fail", "error": str(e)}

def line_hao_report(event_id: str, cron_mode: bool = True):
    try:
        hao_report(event_id, cron_mode)
        return {"result": "success"}
    except Exception as e:
        return {"result": "fail", "error": str(e)}

def handle_join(event:JoinEvent):
    """Handle join event from Line bot

    Args:
        event (JoinEvent): Join event from Line bot
    """
    """_, event_id = get_event_id(event)
    push_message(to=event_id, message=welcome_message)"""
    event_type, event_id = get_event_id(event)
    print(f"Event_type: {event_type}, Event_id: {event_id}")
        
def handle_follow(event:FollowEvent):
    """Handle follow event from Line bot

    Args:
        event (FollowEvent): Follow event from Line bot
    """
    # push_message(to=event_id, message=welcome_message)
    event_type, event_id = get_event_id(event)
    print(f"Event_type: {event_type}, Event_id: {event_id}")

else_message = "請輸入正確指令，或輸入'幫助'查看指令"

help_message = """法人與期貨更新時間: 15:05
籌碼更新時間: 21:00
-----------------------------
日報指令:
- 法人: 查看今日法人買賣超
- 期貨: 查看今日期貨資訊
- 籌碼: 查看今日融資融券資訊
影片指令:
- hao: 查看今日財金皓角總結
-----------------------------
基本指令:
- 幫助: 查看指令"""

welcome_message = f"歡迎使用 Line 股票追蹤機器人！\n\n{help_message}"