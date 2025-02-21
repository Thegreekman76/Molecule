from sqlalchemy import Column, JSON, Integer, String, ForeignKey, Boolean, DateTime, Text, Float, Numeric, func, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship, Mapped
from typing import Optional, List
from datetime import datetime
from core.database.base import Base

class IssueHistory(Base):
    """Model for table issue_history"""
    __tablename__ = 'issue_history'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    issue_id = Column(Integer, nullable=False)
    field_changed = Column(String(50), nullable=False)
    old_value = Column(Text)
    new_value = Column(Text)
    changed_by = Column(Integer, nullable=False)