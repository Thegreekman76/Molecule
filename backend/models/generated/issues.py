from sqlalchemy import Column, JSON, Integer, String, ForeignKey, Boolean, DateTime, Text, Float, Numeric, func, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship, Mapped
from typing import Optional, List
from datetime import datetime
from core.database.base import Base

class Issues(Base):
    """Model for table issues"""
    __tablename__ = 'issues'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    status = Column(String(20), nullable=False, default='open')
    priority = Column(String(20), nullable=False, default='medium')
    type = Column(String(20), nullable=False, default='bug')
    assigned_to = Column(Integer)
    due_date = Column(DateTime)
    estimated_hours = Column(Float)