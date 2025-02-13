from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship
from core.database.base import Base


class UserRoles(Base):
    """Model for table user_roles"""
    __tablename__ = 'user_roles'

    user_id = Column(ForeignKey('users.id'))
    role_id = Column(ForeignKey('roles.id'))
    users = relationship('Users')
    roles = relationship('Roles')