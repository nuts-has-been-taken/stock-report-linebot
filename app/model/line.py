from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

Base = declarative_base()

# Line Users table
class LineUser(Base):
    __tablename__ = "line_user"

    user_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=True)
    line_id = Column(String, nullable=False)
    line_type = Column(String, nullable=False)
    user_class = Column(String, nullable=True)
    credit = Column(Integer, default=0)

# Invoice table
class Invoice(Base):
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
    line_user = relationship("LineUser")
    
class DailyReport(Base):
    __tablename__ = "daily_report"

    user_id = Column(Integer, ForeignKey("line_user.user_id"), nullable=False, primary_key=True)
    line_id = Column(String, ForeignKey("line_user.line_id"), nullable=False)
    futures = Column(Boolean, default=False)
    margin = Column(Boolean, default=False)
    major_invest = Column(Boolean, default=False)