from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship
from core.database.base import Base


class Comments(Base):
    """Model for table comments"""
    __tablename__ = 'comments'

    id = Column(Integer, nullable=False, default=nextval('"public".comments_id_seq'::regclass))
    content = Column(String, nullable=False)
    author_id = Column(Integer, nullable=False)
    issue_id = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=CURRENT_TIMESTAMP)
    updated_at = Column(DateTime)