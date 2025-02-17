from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship
from core.database.base import Base


class Projects(Base):
    """Model for table projects"""
    __tablename__ = 'projects'

    id = Column(Integer, nullable=False, default=nextval('"public".projects_id_seq'::regclass))
    description = Column(String)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    created_at = Column(DateTime, default=CURRENT_TIMESTAMP)
    updated_at = Column(DateTime)