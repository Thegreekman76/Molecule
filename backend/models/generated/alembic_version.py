from sqlalchemy import Column, JSON, Integer, String, ForeignKey, Boolean, DateTime, Text, Float, Numeric, func, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship, Mapped
from typing import Optional, List
from datetime import datetime
from core.database.base import Base

class AlembicVersion(Base):
    """Model for table alembic_version"""
    __tablename__ = 'alembic_version'
    __table_args__ = {'extend_existing': True}

    version_num = Column(String(32), nullable=False)