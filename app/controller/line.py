from linebot.models import MessageEvent, JoinEvent, FollowEvent

from app.service.line import register_user
from app.util.line import get_event_id

def handle_msg(event:MessageEvent):
    """Handle message event from Line bot

    Args:
        event (MessageEvent): Message event from Line bot
    """
    if event.message.text == "註冊":
        register_user(event=event)
    elif event.message.text == "":
        pass

def handle_join(event:JoinEvent):
    """Handle join event from Line bot

    Args:
        event (JoinEvent): Join event from Line bot
    """
    event_id = get_event_id(event)
    pass
        
def handle_follow(event:FollowEvent):
    """Handle follow event from Line bot

    Args:
        event (FollowEvent): Follow event from Line bot
    """
    event_id = get_event_id(event)
    pass