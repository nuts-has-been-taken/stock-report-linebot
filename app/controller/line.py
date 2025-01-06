from linebot.models import MessageEvent, JoinEvent, FollowEvent

from app.service.line import register_user, check_user_class, check_user_register, daily_report, subscribe_daily_report
from app.util.line import get_event_id, push_message

def handle_msg(event:MessageEvent):
    """Handle message event from Line bot

    Args:
        event (MessageEvent): Message event from Line bot
    """
    # 註冊
    event_id = get_event_id(event)[1]
    if event.message.text == "註冊":
        if not check_user_register(user_id=event_id):
            if register_user(event=event):
                push_message(to=event_id, message=user_register_complete_message)
            else:
                push_message(to=event_id, message="註冊失敗")
        else:
            push_message(to=event_id, message="已註冊過")
    # 訂閱
    elif event.message.text == "訂閱日報":
        if check_user_register(user_id=event_id):
            user_class = check_user_class(user_id=event_id)
            if user_class: # 判斷用戶階級
                pass #TODO
            else:
                push_message(to=event_id, message="請提升用戶等級已啟用訂閱功能")
        else:
            push_message(to=event_id, message="請先註冊")
    # 日報
    elif event.message.text in ["法人", "籌碼", "期貨"]:
        daily_report(user_id=event_id, report_type=event.message.text)
        pass # TODO
    # 幫助
    elif event.message.text == "幫助":
        push_message(to=event_id, message=help_message)
    else:
        # 聊天室或群組一般聊天不回覆
        if event.source.type == "user":
            push_message(to=get_event_id(event)[1], message=else_message)

def handle_join(event:JoinEvent):
    """Handle join event from Line bot

    Args:
        event (JoinEvent): Join event from Line bot
    """
    _, event_id = get_event_id(event)
    push_message(to=event_id, message=welcome_message)
        
def handle_follow(event:FollowEvent):
    """Handle follow event from Line bot

    Args:
        event (FollowEvent): Follow event from Line bot
    """
    _, event_id = get_event_id(event)
    push_message(to=event_id, message=welcome_message)

else_message = "請輸入正確指令，或輸入'幫助'查看指令"

help_message = """輸入以下指令即可使用功能
法人與期貨更新時間: 15:05
籌碼更新時間: 21:00
日報指令:
- 法人:查看今日法人買賣超
- 期貨:查看今日期貨資訊
- 籌碼:查看今日融資融券資訊
基本指令:
- 註冊:註冊用戶啟用更多功能
- 幫助:查看指令
更多指令:
- 訂閱日報:每日指定時間推送日報
  ex.訂閱日報 [法人,籌碼,期貨]
- 取消日報:取消推送日報
"""

user_register_complete_message = "註冊成功！請輸入'幫助'查看指令"

welcome_message = f"歡迎使用 Line 股票機器人！\n {help_message}"