from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship
from core.database.base import Base


class UserRoles(Base):
    """Model for table user_roles"""
    __tablename__ = 'user_roles'

    id = Column(Integer, nullable=False, default=nextval('"public".user_roles_id_seq'::regclass))
    user_id = Column(ForeignKey('users.id'), nullable=False, unique=True)
    role_id = Column(ForeignKey('roles.id'), nullable=False, unique=True)
    created_at = Column(DateTime, default=CURRENT_TIMESTAMP)
    updated_at = Column(DateTime, default=CURRENT_TIMESTAMP)
    users = relationship('Users')
    roles = relationship('Roles')