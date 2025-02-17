from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship
from core.database.base import Base


class IssueTags(Base):
    """Model for table issue_tags"""
    __tablename__ = 'issue_tags'

    id = Column(Integer, nullable=False, default=nextval('"public".issue_tags_id_seq'::regclass))
    issue_id = Column(Integer, nullable=False)
    tag_id = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=CURRENT_TIMESTAMP)
    updated_at = Column(DateTime)