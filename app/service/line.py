
from app.util.line import push_message
from app.db.report import get_today_report
from app.service.report import create_major_investors_report, create_futures_report, create_margin_report
from app.service.youtube import get_today_hao_report

def daily_report(event_id:str, report_type:str, data_number=20):
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
            push_message(to=event_id, message=f"{report_type} daily report 查詢失敗，錯誤訊息: {error_msg}")
            return
    result = get_today_report(report_type)
    push_message(to=event_id, message=result.msg, img_url=result.url)
    return

def hao_report(event_id:str):
    """Send Hao report to event"""
    success, data, err_msg = get_today_hao_report()
    if success:
        push_message(to=event_id, message=data.vid_summary)
    else:
        push_message(to=event_id, message=f"財金皓角 daily report 查詢失敗，錯誤訊息: {err_msg}")
    return 