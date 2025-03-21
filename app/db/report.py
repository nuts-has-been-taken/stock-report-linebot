from app.core.config import postgress_db
from app.model.model import Report

import datetime

Session = postgress_db.SESSION

def save_report(date, report_type, msg, url):
    """Save a report to the database
    
    Args:
        date (datetime.date): The date of the report
        report_type (str): The type of the report
        msg (str): The message or description of the report
        url (str): The URL of the report image
    
    Returns:
        bool: True if the report was saved successfully, False otherwise
    """
    session = Session()
    try:
        new_report = Report(
            date=date,
            type=report_type,
            msg=msg,
            url=url
        )
        session.add(new_report)
        session.commit()
        return None
    except Exception as e:
        session.rollback()
        print(f"Error saving report: {e}")
        return e
    finally:
        session.close()

def get_today_report(report_type:str):
    """Get today report from database
    
    Args:
        report_type (str): Report type
    
    Returns:
        dict: Report data
    """
    session = Session()
    today = datetime.date.today()
    results = session.query(Report).filter(Report.date == today, Report.type == report_type).all()
    session.close()
    if results:
        return results[0]
    else:
        return None