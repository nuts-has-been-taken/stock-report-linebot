from sqlalchemy import Column, Integer, String, Date, Enum, Boolean, ForeignKey, DateTime, Float, BigInteger, DECIMAL, Index
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

class CompanyFinancialMetrics(Base):
    __tablename__ = 'company_financial_metrics'

    # 基本識別資訊
    stock_code = Column(String(10), primary_key=True, nullable=False)
    company_name = Column(String(255))
    sector = Column(String(100))  # yfinance sector
    industry = Column(String(100))  # yfinance industry
    update_date = Column(Date, nullable=False)  # 資料日期

    # 盈利能力指標 (6個)
    revenue_growth_rate = Column(DECIMAL(10, 4))  # 營收成長率 (%)
    gross_margin = Column(DECIMAL(10, 4))  # 毛利率 (%)
    net_margin = Column(DECIMAL(10, 4))  # 淨利率 (%)
    operating_margin = Column(DECIMAL(10, 4))  # 營業利益率 (%)
    roa = Column(DECIMAL(10, 4))  # 資產報酬率 (%)
    roe = Column(DECIMAL(10, 4))  # 股東權益報酬率 (%)

    # 每股指標 (2個)
    eps = Column(DECIMAL(10, 4))  # 每股盈餘
    eps_growth = Column(DECIMAL(10, 4))  # EPS成長率 (%)

    # 現金流指標 (1個)
    ocf_to_net_income = Column(DECIMAL(10, 4))  # 現金流對淨利比

    # 財務結構指標 (2個)
    debt_ratio = Column(DECIMAL(10, 4))  # 負債比 (%)
    current_ratio = Column(DECIMAL(10, 4))  # 流動比率

    # 額外有用的原始數據 (用於計算和驗證)
    book_value_per_share = Column(DECIMAL(10, 4))  # 每股淨值
    operating_cash_flow = Column(BigInteger)  # 營運現金流
    free_cash_flow = Column(BigInteger)  # 自由現金流
    interest_coverage = Column(DECIMAL(10, 4))  # 利息保障倍數

    __table_args__ = (
        Index('idx_sector', 'sector'),
        Index('idx_company_name', 'company_name'),
    )