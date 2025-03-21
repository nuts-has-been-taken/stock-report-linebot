
from app.util.line import push_message
from app.db.report import get_today_report
from app.service.daily_report import create_major_investors_report, create_futures_report, create_margin_report

def daily_report(event_id:str, report_type:str) -> bool:
    """Send daily report to event"""
    send_major_investors_report(event_id, report_type)
    
    return

def send_major_investors_report(event_id:str, report_type:str, data_number=20):
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
            push_message(to=event_id, message=f"查詢失敗，錯誤訊息:{error_msg}")
            return
    result = get_today_report(report_type)
    push_message(to=event_id, message=result.msg, img_url=result.url)
    return