from sqlalchemy import Column, JSON, Integer, String, ForeignKey, Boolean, DateTime, Text, Float, Numeric, func, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship, Mapped
from typing import Optional, List
from datetime import datetime
from core.database.base import Base

class Projects(Base):
    """Model for table projects"""
    __tablename__ = 'projects'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    name = Column(String(100), nullable=False)
    description = Column(Text)
    status = Column(String(20), nullable=False, default='active')
    start_date = Column(DateTime)
    end_date = Column(DateTime)