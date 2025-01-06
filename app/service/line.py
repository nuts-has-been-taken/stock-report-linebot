from linebot.models import MessageEvent

def register_user(event:MessageEvent):
    """Register user to database"""
    
    if event.source.type == "user":
        user_id = event.source.user_id
        print(f"用戶 ID: {user_id}")
    elif event.source.type == "group":
        group_id = event.source.group_id
        print(f"群組 ID: {group_id}")
    elif event.source.type == "room":
        room_id = event.source.room_id
        print(f"聊天室 ID: {room_id}")

def daily_report(user_id:str, report_type:str):
    """Send daily report to user"""
    pass

def subscribe_daily_report(user_id:str, subscrible_list:list):
    """Subscribe daily report to user"""
    pass

def check_user_register(user_id:str):
    """Check user register"""
    pass

def check_user_class(user_id:str):
    """Check user class"""
    pass