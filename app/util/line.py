from linebot.models import TextSendMessage, Event

from app.core.config import line_bot

def reply_message(reply_token:str, message:str):
    """Reply message to user

    Args:
        reply_token (str): Reply token
        message (str): Message to reply
    """
    line_bot.LINE_BOT_API.reply_message(reply_token, TextSendMessage(text=message))

def push_message(to:str, message:str):
    """Push message to user

    Args:
        to (str): User ID
        message (str): Message to push
    """
    line_bot.LINE_BOT_API.push_message(to, TextSendMessage(text=message))

def get_event_id(event:Event):
    """Get event ID

    Args:
        event (MessageEvent): Message event from Line bot

    Returns:
        str: Event ID
    """
    if event.source.type == "user":
        return event.source.user_id
    elif event.source.type == "group":
        return event.source.group_id
    elif event.source.type == "room":
        return event.source.room_id
    else:
        return None

def get_reply_token(event:Event):
    """Get reply token

    Args:
        event (MessageEvent): Message event from Line bot

    Returns:
        str: Reply token
    """
    return event.reply_token