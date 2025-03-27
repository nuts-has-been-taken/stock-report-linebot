from linebot.models import TextSendMessage, Event, ImageSendMessage, FlexSendMessage

from app.core.config import line_bot

def reply_message(reply_token:str, message:str):
    """Reply message to user

    Args:
        reply_token (str): Reply token
        message (str): Message to reply
    """
    line_bot.LINE_BOT_API.reply_message(reply_token, TextSendMessage(text=message))

def push_message(to:str, message:str=None, img_url:str=None, flex_msg:dict=None):
    """Push message to user

    Args:
        to (str): User ID
        message (str): Message to push
        image_url (str): Image URL to push
    """
    messages = []
    
    # 如果有文字訊息
    if message:
        messages.append(TextSendMessage(text=message))
    
    # 如果有圖片訊息
    if img_url:
        messages.append(ImageSendMessage(original_content_url=img_url, preview_image_url=img_url))

    # 推送訊息
    if messages:
        line_bot.LINE_BOT_API.push_message(to, messages)
    
    # 如果有 Flex 訊息
    if flex_msg:
        line_bot.LINE_BOT_API.push_message(to, FlexSendMessage(alt_text="Flex message", contents=flex_msg))

def get_event_id(event:Event):
    """Get event ID

    Args:
        event (MessageEvent): Message event from Line bot

    Returns:
        str: Event type
        str: Event ID
    """
    if event.source.type == "user":
        return event.source.type, event.source.user_id
    elif event.source.type == "group":
        return event.source.type, event.source.group_id
    elif event.source.type == "room":
        return event.source.type, event.source.room_id
    else:
        return None, None

def get_reply_token(event:Event):
    """Get reply token

    Args:
        event (MessageEvent): Message event from Line bot

    Returns:
        str: Reply token
    """
    return event.reply_token