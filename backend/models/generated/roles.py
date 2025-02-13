from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship
from core.database.base import Base


class Roles(Base):
    """Model for table roles"""
    __tablename__ = 'roles'

    id = Column(Integer, nullable=False, default=nextval('"public".roles_id_seq'::regclass))
    name = Column(String)
    description = Column(String)
    is_active = Column(Boolean)
    created_at = Column(DateTime, nullable=False, default=CURRENT_TIMESTAMP)
    updated_at = Column(DateTime, nullable=False, default=CURRENT_TIMESTAMP)