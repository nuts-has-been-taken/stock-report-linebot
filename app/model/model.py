from sqlalchemy import Column, Integer, String, Date, Enum, Boolean, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import enum

Base = declarative_base()

class ReportType(enum.Enum):
    法人 = "法人"
    籌碼 = "籌碼"
    期貨 = "期貨"

# Report table
class Report(Base):
    __tablename__ = 'reports'

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date, default=datetime.today, nullable=False)
    type = Column(Enum(ReportType), nullable=False)
    msg = Column(String, nullable=False)
    url = Column(String, nullable=False)

# Daily Major Invest table
class DailyMajorInvest(Base):
    __tablename__ = 'daily_major_invest'

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date, default=datetime.today, nullable=False)
    foreign_investors = Column(Integer, nullable=False)
    investment_trust = Column(Integer, nullable=False)
    dealer = Column(Integer, nullable=False)

# Daily Margin table
class DailyMargin(Base):
    __tablename__ = 'daily_margin'

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date, default=datetime.today, nullable=False)
    margin_ticket = Column(Integer, nullable=False)
    margin_amount = Column(Integer, nullable=False)

# Daily Future table
class DailyFuture(Base):
    __tablename__ = 'daily_future'

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date, default=datetime.today, nullable=False)
    foreign_investors = Column(Integer, nullable=False)
    investment_trust = Column(Integer, nullable=False)
    dealer = Column(Integer, nullable=False)

# imgur token table
class ImgurToken(Base):
    __tablename__ = 'imgur_tokens'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    refresh_token = Column(String, nullable=False)
    date = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)
    access_token = Column(String, nullable=True)

class YouTubeVideo(Base):
    __tablename__ = 'youtube_videos'

    id = Column(Integer, primary_key=True, autoincrement=True)
    channel_name = Column(String, nullable=False)
    channel_id = Column(String, nullable=False)
    date = Column(Date, nullable=False)
    vid_name = Column(String, nullable=False)
    vid_url = Column(String, nullable=False)
    vid_summary = Column(String, nullable=True)

# Line Users table (deprecated)
"""class LineUser(Base):
    __tablename__ = "line_user"

    user_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=True)
    line_id = Column(String, nullable=False, unique=True)
    line_type = Column(String, nullable=False)
    user_class = Column(String, nullable=True)
    credit = Column(Integer, default=0)"""

# Invoice table (deprecated)
"""class Invoice(Base):
    __tablename__ = "invoice"

    user_id = Column(Integer, ForeignKey("line_user.user_id"), nullable=False)
    invoice_id = Column(Integer, unique=True, nullable=False, primary_key=True)
    payment = Column(String, nullable=False)
    payment_reference = Column(String, nullable=False)
    price = Column(Integer, nullable=False)
    status = Column(String, nullable=False)
    create_at = Column(DateTime, default=datetime.now(timezone.utc))
    update_at = Column(DateTime, default=datetime.now(timezone.utc))
    description = Column(String, nullable=True)
    line_user = relationship("LineUser")"""

# Daily report table (deprecated)
"""class DailyReport(Base):
    __tablename__ = "daily_report"

    line_id = Column(String, nullable=False, primary_key=True)
    futures = Column(Boolean, default=False)
    margin = Column(Boolean, default=False)
    major_invest = Column(Boolean, default=False)"""