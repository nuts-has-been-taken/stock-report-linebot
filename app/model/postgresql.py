from sqlalchemy import Column, Integer, String, Date, Enum, Boolean, ForeignKey, DateTime, Float, BigInteger
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
    foreign_investors = Column(BigInteger, nullable=False)
    investment_trust = Column(BigInteger, nullable=False)
    dealer = Column(BigInteger, nullable=False)

# Daily Margin table
class DailyMargin(Base):
    __tablename__ = 'daily_margin'

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date, default=datetime.today, nullable=False)
    margin_ticket = Column(BigInteger, nullable=False)
    margin_amount = Column(Float, nullable=False)

# Daily Future table
class DailyFuture(Base):
    __tablename__ = 'daily_future'

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date, default=datetime.today, nullable=False)
    foreign_investors = Column(BigInteger, nullable=False)
    investment_trust = Column(BigInteger, nullable=False)
    dealer = Column(BigInteger, nullable=False)

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
    vid_img = Column(String, nullable=True)