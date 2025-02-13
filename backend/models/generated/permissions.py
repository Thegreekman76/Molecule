from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship
from core.database.base import Base


class Permissions(Base):
    """Model for table permissions"""
    __tablename__ = 'permissions'

    id = Column(Integer, nullable=False, default=nextval('"public".permissions_id_seq'::regclass))
    name = Column(String)
    description = Column(String)
    resource = Column(String)
    action = Column(String)
    created_at = Column(DateTime, nullable=False, default=CURRENT_TIMESTAMP)
    updated_at = Column(DateTime, nullable=False, default=CURRENT_TIMESTAMP)