from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship
from core.database.base import Base


class Tags(Base):
    """Model for table tags"""
    __tablename__ = 'tags'

    id = Column(Integer, nullable=False, default=nextval('"public".tags_id_seq'::regclass))
    created_at = Column(DateTime, default=CURRENT_TIMESTAMP)
    updated_at = Column(DateTime)