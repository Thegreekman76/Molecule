# core/security/roles.py
from sqlalchemy import Column, Integer, String, Table, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from core.database.base import Base

# Tabla de asociación entre roles y permisos
role_permissions = Table(
    'role_permissions',
    Base.metadata,
    Column('role_id', Integer, ForeignKey('roles.id')),
    Column('permission_id', Integer, ForeignKey('permissions.id'))
)

# Tabla de asociación entre usuarios y roles
user_roles = Table(
    'user_roles',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('role_id', Integer, ForeignKey('roles.id'))
)

class Role(Base):
    __tablename__ = 'roles'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Relaciones
    permissions = relationship('Permission', secondary=role_permissions, back_populates='roles')
    users = relationship('UserModel', secondary=user_roles, back_populates='roles')

class Permission(Base):
    __tablename__ = 'permissions'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(String, nullable=True)
    resource = Column(String)  # Recurso al que aplica el permiso
    action = Column(String)    # Acción permitida (create, read, update, delete)
    
    # Relaciones
    roles = relationship('Role', secondary=role_permissions, back_populates='permissions')