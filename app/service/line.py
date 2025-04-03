
from app.util.line import push_message
from app.db.report import get_today_report
from app.service.report import create_major_investors_report, create_futures_report, create_margin_report
from app.service.youtube import get_today_hao_report

from datetime import datetime
import copy
import re

daily_report_felx_msg = {
    "type": "bubble",
    "header": {
        "type": "box",
        "layout": "vertical",
        "contents": [
            {
                "type": "text",
                "text": "【股票報告】2025-03-26",
                "size": "sm",
                "align": "start",
                "color": "#FFFCEC"
            }
        ],
        "borderWidth": "none",
        "backgroundColor": "#2894FF",
        "cornerRadius": "none",
        "paddingStart": "lg",
        "paddingBottom": "md",
        "paddingTop": "lg"
    },
    "hero": {
        "type": "image",
        "size": "full",
        "aspectMode": "cover",
        "action": {
            "type": "uri",
            "label": "action",
            "uri": "https://i.imgur.com/q1r8GO1.png"
        },
        "aspectRatio": "20:13",
        "url": "https://i.imgur.com/q1r8GO1.png"
    },
    "body": {
        "type": "box",
        "layout": "vertical",
        "contents": [
            {
                "type": "text",
                "text": "三大法人買賣超變化",
                "weight": "bold",
                "size": "xl"
            },
            {
                "type": "text",
                "text": "外資：-2.3 億 \n投信：35.7 億 \n自營商：8.5 億",
                "color": "#666666",
                "size": "sm",
                "flex": 1,
                "weight": "regular",
                "style": "normal",
                "decoration": "none",
                "wrap": True,
                "offsetTop": "sm"
            }
        ],
        "paddingTop": "none",
        "paddingBottom": "lg"
    }
}

report_dict = {
    "法人":"三大法人買賣超變化",
    "籌碼":"融資融券餘額變化",
    "期貨":"三大法人期貨未平倉口數"
}

hao_report_flex_msg = {
    "type": "bubble",
    "header": {
        "type": "box",
        "layout": "vertical",
        "contents": [
            {
                "type": "text",
                "text": "【游庭皓的財經皓角】 2025-03-28 報告",
                "size": "sm",
                "align": "start",
                "color": "#FFFCEC"
            }
        ],
        "borderWidth": "none",
        "backgroundColor": "#FF5151",
        "cornerRadius": "none",
        "paddingStart": "lg",
        "paddingBottom": "md",
        "paddingTop": "lg"
    },
    "hero": {
        "type": "image",
        "url": "https://i.imgur.com/q1r8GO1.png",
        "aspectMode": "fit",
        "aspectRatio": "17.7:10",
        "size": "full",
        "action": {
            "type": "uri",
            "label": "action",
            "uri": "https://i.imgur.com/q1r8GO1.png"
        },
    },
    "body": {
        "type": "box",
        "layout": "vertical",
        "contents": [
            {
                "type": "text",
                "text": "重點摘要",
                "weight": "bold",
                "size": "xl"
            },
            {
                "type": "text",
                "text": "None",
                "color": "#666666",
                "size": "sm",
                "flex": 1,
                "weight": "regular",
                "style": "normal",
                "decoration": "none",
                "wrap": True,
                "offsetTop": "none"
            },
            {
                "type": "separator",
                "margin": "md"
            },
            {
                "type": "text",
                "text": "AI看法",
                "weight": "bold",
                "size": "xl",
                "offsetTop": "md"
            },
            {
                "type": "text",
                "text": "None",
                "color": "#666666",
                "size": "sm",
                "flex": 1,
                "weight": "regular",
                "style": "normal",
                "decoration": "none",
                "wrap": True,
                "offsetTop": "md"
            }
        ],
        "paddingBottom": "xl",
        "paddingTop": "md"
    }
}

def fetch_daily_report(event_id:str, report_type:str, data_number=20, cron_mode:bool = False):
    """Send daily report to event"""
    # TODO 時間檢查
    
    result = get_today_report(report_type)
    if not result:
        print(f"====生成{report_type}報告====")
        if report_type == "法人":
            error_msg = create_major_investors_report(data_number)
        elif report_type == "籌碼":
            error_msg = create_margin_report(data_number)
        elif report_type == "期貨":
            error_msg = create_futures_report(data_number)
        if error_msg:
            print(f"{report_type} daily report 查詢失敗，錯誤訊息: {error_msg}")
            if not cron_mode:
                push_message(to=event_id, message=f"{report_type} daily report 查詢失敗，錯誤訊息: {error_msg}")
            return
    result = get_today_report(report_type)
    # 組裝 Flex Message
    flex_copy = copy.deepcopy(daily_report_felx_msg)
    flex_copy["header"]["contents"][0]["text"] = f"【股票報告】 {result.date.strftime('%Y-%m-%d')}"
    flex_copy["hero"]["action"]["uri"] = result.url
    flex_copy["hero"]["url"] = result.url
    flex_copy["body"]["contents"][0]["text"] = report_dict[report_type]
    flex_copy["body"]["contents"][1]["text"] = result.msg
    push_message(to=event_id, flex_msg=flex_copy, alt_text=f"【股票報告】{report_dict[report_type]}")
    return

def hao_report(event_id:str, cron_mode:bool = True):
    """Send Hao report to event"""
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0).strftime('%Y-%m-%d')
    success, data, err_msg = get_today_hao_report()
    if success:
        sections = re.split(r'### .+?：', data.vid_summary)
        contents = [section.strip() for section in sections if section.strip()]
        flex_copy = copy.deepcopy(hao_report_flex_msg)
        flex_copy["header"]["contents"][0]["text"] = f"【游庭皓的財經皓角】 {today} 報告"
        flex_copy["hero"]["url"] = data.vid_img
        flex_copy["hero"]["action"]["uri"] = data.vid_url
        flex_copy["body"]["contents"][1]["text"] = contents[0]
        flex_copy["body"]["contents"][4]["text"] = contents[1]
        push_message(to=event_id, flex_msg=flex_copy, alt_text=f"【游庭皓的財經皓角】報告")
    else:
        if not cron_mode:
            push_message(to=event_id, message=f"財金皓角 daily report 查詢失敗，錯誤訊息: {err_msg}")
    return 