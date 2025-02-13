from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship
from core.database.base import Base


class RolePermissions(Base):
    """Model for table role_permissions"""
    __tablename__ = 'role_permissions'

    role_id = Column(ForeignKey('roles.id'))
    permission_id = Column(ForeignKey('permissions.id'))
    roles = relationship('Roles')
    permissions = relationship('Permissions')