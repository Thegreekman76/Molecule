from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship
from core.database.base import Base


class Issues(Base):
    """Model for table issues"""
    __tablename__ = 'issues'

    id = Column(Integer, nullable=False, default=nextval('"public".issues_id_seq'::regclass))
    description = Column(String, nullable=False)
    assigned_to = Column(Integer)
    due_date = Column(DateTime)
    estimated_hours = Column(String)
    created_at = Column(DateTime, default=CURRENT_TIMESTAMP)
    updated_at = Column(DateTime)