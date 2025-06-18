from app.core.config import postgress_db
from app.model.postgresql import Report, DailyMajorInvest, DailyMargin, DailyFuture

import datetime

Session = postgress_db.SESSION

def save_daily_major_invest(date, foreign_investors, investment_trust, dealer):
    """Save a DailyMajorInvest record to the database
    
    Args:
        date (datetime.date): The date of the record
        foreign_investors (int): Foreign investors' data
        investment_trust (int): Investment trust data
        dealer (int): Dealer data
    """
    session = Session()
    try:
        new_record = DailyMajorInvest(
            date=date,
            foreign_investors=foreign_investors,
            investment_trust=investment_trust,
            dealer=dealer
        )
        session.add(new_record)
        session.commit()
        return None
    except Exception as e:
        session.rollback()
        print(f"Error saving {date} DailyMajorInvest: {e}")
        return e
    finally:
        session.close()
        
def get_daily_major_invest(date):
    """Get the first DailyMajorInvest record for a specific date
    
    Args:
        date (datetime.date): The date of the record
    
    Returns:
        DailyMajorInvest: The first record for the specified date, or None if not found
    """
    session = Session()
    try:
        result = session.query(DailyMajorInvest).filter(DailyMajorInvest.date == date).first()
        return result
    except Exception as e:
        print(f"Error fetching DailyMajorInvest: {e}")
        return None
    finally:
        session.close()
        
def save_daily_margin(date, margin_ticket, margin_amount):
    """Save a DailyMargin record to the database
    
    Args:
        date (datetime.date): The date of the record
        margin_ticket (int): Margin ticket data
        margin_amount (int): Margin amount data
    """
    session = Session()
    try:
        new_record = DailyMargin(
            date=date,
            margin_ticket=margin_ticket,
            margin_amount=margin_amount
        )
        session.add(new_record)
        session.commit()
        return None
    except Exception as e:
        session.rollback()
        print(f"Error saving {date} DailyMargin: {e}")
        return e
    finally:
        session.close()

def get_daily_margin(date):
    """Get the first DailyMargin record for a specific date
    
    Args:
        date (datetime.date): The date of the record
    
    Returns:
        DailyMargin: The first record for the specified date, or None if not found
    """
    session = Session()
    try:
        result = session.query(DailyMargin).filter(DailyMargin.date == date).first()
        return result
    except Exception as e:
        print(f"Error fetching DailyMargin: {e}")
        return None
    finally:
        session.close()
        
def save_daily_future(date, foreign_investors, investment_trust, dealer):
    """Save a DailyFuture record to the database
    
    Args:
        date (datetime.date): The date of the record
        foreign_investors (int): Foreign investors' data
        investment_trust (int): Investment trust data
        dealer (int): Dealer data
    """
    session = Session()
    try:
        new_record = DailyFuture(
            date=date,
            foreign_investors=foreign_investors,
            investment_trust=investment_trust,
            dealer=dealer
        )
        session.add(new_record)
        session.commit()
        return None
    except Exception as e:
        session.rollback()
        print(f"Error saving {date} DailyFuture: {e}")
        return e
    finally:
        session.close()

def get_daily_future(date):
    """Get the first DailyFuture record for a specific date
    
    Args:
        date (datetime.date): The date of the record
    
    Returns:
        DailyFuture: The first record for the specified date, or None if not found
    """
    session = Session()
    try:
        result = session.query(DailyFuture).filter(DailyFuture.date == date).first()
        return result
    except Exception as e:
        print(f"Error fetching DailyFuture: {e}")
        return None
    finally:
        session.close()
        
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