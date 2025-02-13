from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship
from core.database.base import Base


class Users(Base):
    """Model for table users"""
    __tablename__ = 'users'

    id = Column(Integer, nullable=False, default=nextval('"public".users_id_seq'::regclass))
    username = Column(String)
    email = Column(String)
    full_name = Column(String)
    hashed_password = Column(String)
    is_active = Column(Boolean)
    is_superuser = Column(Boolean)
    created_at = Column(DateTime, nullable=False, default=CURRENT_TIMESTAMP)
    updated_at = Column(DateTime, nullable=False, default=CURRENT_TIMESTAMP)