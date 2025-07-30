from app.core.config import postgress_db
from app.model.postgresql import Report, DailyMajorInvest, DailyMargin, DailyFuture
from contextlib import contextmanager
from typing import Generator, Optional
from sqlalchemy.orm import Session as SQLSession

import datetime

Session = postgress_db.SESSION

@contextmanager
def get_db_session() -> Generator[SQLSession, None, None]:
    """Database session context manager for proper resource cleanup."""
    session = postgress_db.SESSION()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

def save_daily_major_invest(
    date: datetime.date, 
    foreign_investors: int, 
    investment_trust: int, 
    dealer: int
) -> Optional[Exception]:
    """Save a DailyMajorInvest record to the database
    
    Args:
        date (datetime.date): The date of the record
        foreign_investors (int): Foreign investors' data
        investment_trust (int): Investment trust data
        dealer (int): Dealer data
    
    Returns:
        Optional[Exception]: None if successful, Exception if error occurred
    """
    try:
        with get_db_session() as session:
            new_record = DailyMajorInvest(
                date=date,
                foreign_investors=foreign_investors,
                investment_trust=investment_trust,
                dealer=dealer
            )
            session.add(new_record)
        return None
    except Exception as e:
        print(f"Error saving {date} DailyMajorInvest: {e}")
        return e
        
def get_daily_major_invest(date: datetime.date) -> Optional[DailyMajorInvest]:
    """Get the first DailyMajorInvest record for a specific date
    
    Args:
        date (datetime.date): The date of the record
    
    Returns:
        Optional[DailyMajorInvest]: The first record for the specified date, or None if not found
    """
    try:
        with get_db_session() as session:
            result = session.query(DailyMajorInvest).filter(DailyMajorInvest.date == date).first()
            return result
    except Exception as e:
        print(f"Error fetching DailyMajorInvest: {e}")
        return None
        
def save_daily_margin(
    date: datetime.date, 
    margin_ticket: int, 
    margin_amount: int
) -> Optional[Exception]:
    """Save a DailyMargin record to the database
    
    Args:
        date (datetime.date): The date of the record
        margin_ticket (int): Margin ticket data
        margin_amount (int): Margin amount data
    
    Returns:
        Optional[Exception]: None if successful, Exception if error occurred
    """
    try:
        with get_db_session() as session:
            new_record = DailyMargin(
                date=date,
                margin_ticket=margin_ticket,
                margin_amount=margin_amount
            )
            session.add(new_record)
        return None
    except Exception as e:
        print(f"Error saving {date} DailyMargin: {e}")
        return e

def get_daily_margin(date: datetime.date) -> Optional[DailyMargin]:
    """Get the first DailyMargin record for a specific date
    
    Args:
        date (datetime.date): The date of the record
    
    Returns:
        Optional[DailyMargin]: The first record for the specified date, or None if not found
    """
    try:
        with get_db_session() as session:
            result = session.query(DailyMargin).filter(DailyMargin.date == date).first()
            return result
    except Exception as e:
        print(f"Error fetching DailyMargin: {e}")
        return None
        
def save_daily_future(
    date: datetime.date, 
    foreign_investors: int, 
    investment_trust: int, 
    dealer: int
) -> Optional[Exception]:
    """Save a DailyFuture record to the database
    
    Args:
        date (datetime.date): The date of the record
        foreign_investors (int): Foreign investors' data
        investment_trust (int): Investment trust data
        dealer (int): Dealer data
    
    Returns:
        Optional[Exception]: None if successful, Exception if error occurred
    """
    try:
        with get_db_session() as session:
            new_record = DailyFuture(
                date=date,
                foreign_investors=foreign_investors,
                investment_trust=investment_trust,
                dealer=dealer
            )
            session.add(new_record)
        return None
    except Exception as e:
        print(f"Error saving {date} DailyFuture: {e}")
        return e

def get_daily_future(date: datetime.date) -> Optional[DailyFuture]:
    """Get the first DailyFuture record for a specific date
    
    Args:
        date (datetime.date): The date of the record
    
    Returns:
        Optional[DailyFuture]: The first record for the specified date, or None if not found
    """
    try:
        with get_db_session() as session:
            result = session.query(DailyFuture).filter(DailyFuture.date == date).first()
            return result
    except Exception as e:
        print(f"Error fetching DailyFuture: {e}")
        return None
        
def save_report(
    date: datetime.date, 
    report_type: str, 
    msg: str, 
    url: str
) -> Optional[Exception]:
    """Save a report to the database
    
    Args:
        date (datetime.date): The date of the report
        report_type (str): The type of the report
        msg (str): The message or description of the report
        url (str): The URL of the report image
    
    Returns:
        Optional[Exception]: None if successful, Exception if error occurred
    """
    try:
        with get_db_session() as session:
            new_report = Report(
                date=date,
                type=report_type,
                msg=msg,
                url=url
            )
            session.add(new_report)
        return None
    except Exception as e:
        print(f"Error saving report: {e}")
        return e

def get_today_report(report_type: str) -> Optional[Report]:
    """Get today report from database
    
    Args:
        report_type (str): Report type
    
    Returns:
        Optional[Report]: Report data or None if not found
    """
    try:
        with get_db_session() as session:
            today = datetime.date.today()
            results = session.query(Report).filter(
                Report.date == today, 
                Report.type == report_type
            ).all()
            if results:
                return results[0]
            return None
    except Exception as e:
        print(f"Error fetching today's report: {e}")
        return None
