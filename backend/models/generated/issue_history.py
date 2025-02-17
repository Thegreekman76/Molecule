from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship
from core.database.base import Base


class IssueHistory(Base):
    """Model for table issue_history"""
    __tablename__ = 'issue_history'

    id = Column(Integer, nullable=False, default=nextval('"public".issue_history_id_seq'::regclass))
    issue_id = Column(Integer, nullable=False)
    old_value = Column(String)
    new_value = Column(String)
    changed_by = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=CURRENT_TIMESTAMP)
    updated_at = Column(DateTime)