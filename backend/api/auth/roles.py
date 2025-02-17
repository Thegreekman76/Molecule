# backend\api\auth\roles.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from core.database.database import get_db
from core.security.auth import AuthManager
from core.security.roles import Role, Permission
from core.security.schemas import (
    RoleCreate,
    RoleUpdate,
    Role as RoleSchema,
    Permission as PermissionSchema,
    PermissionCreate
)

router = APIRouter()

# Rutas para Roles
@router.post("/roles/", response_model=RoleSchema)
async def create_role(
    *,
    db: Session = Depends(get_db),
    role_in: RoleCreate,
    current_user = Depends(AuthManager.get_current_admin_user)
):
    """Crear nuevo rol"""
    db_role = Role(
        name=role_in.name,
        description=role_in.description,
        is_active=role_in.is_active
    )
    
    if role_in.permissions:
        permissions = db.query(Permission).filter(
            Permission.id.in_(role_in.permissions)
        ).all()
        db_role.permissions = permissions
    
    db.add(db_role)
    db.commit()
    db.refresh(db_role)
    return db_role

@router.get("/roles/", response_model=List[RoleSchema])
async def read_roles(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user = Depends(AuthManager.get_current_active_user)
):
    """Obtener lista de roles"""
    roles = db.query(Role).offset(skip).limit(limit).all()
    return roles

@router.get("/roles/{role_id}", response_model=RoleSchema)
async def read_role(
    *,
    db: Session = Depends(get_db),
    role_id: int,
    current_user = Depends(AuthManager.get_current_active_user)
):
    """Obtener un rol específico"""
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    return role

@router.put("/roles/{role_id}", response_model=RoleSchema)
async def update_role(
    *,
    db: Session = Depends(get_db),
    role_id: int,
    role_in: RoleUpdate,
    current_user = Depends(AuthManager.get_current_admin_user)
):
    """Actualizar un rol"""
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    
    # Actualizar campos básicos
    for field in role_in.dict(exclude_unset=True, exclude={'permissions'}):
        setattr(role, field, getattr(role_in, field))
    
    # Actualizar permisos si se proporcionaron
    if role_in.permissions is not None:
        permissions = db.query(Permission).filter(
            Permission.id.in_(role_in.permissions)
        ).all()
        role.permissions = permissions
    
    db.add(role)
    db.commit()
    db.refresh(role)
    return role

@router.delete("/roles/{role_id}")
async def delete_role(
    *,
    db: Session = Depends(get_db),
    role_id: int,
    current_user = Depends(AuthManager.get_current_admin_user)
):
    """Eliminar un rol"""
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    
    db.delete(role)
    db.commit()
    return {"ok": True}

# Rutas para Permisos
@router.post("/permissions/", response_model=PermissionSchema)
async def create_permission(
    *,
    db: Session = Depends(get_db),
    permission_in: PermissionCreate,
    current_user = Depends(AuthManager.get_current_admin_user)
):
    """Crear nuevo permiso"""
    db_permission = Permission(**permission_in.dict())
    db.add(db_permission)
    db.commit()
    db.refresh(db_permission)
    return db_permission

@router.get("/permissions/", response_model=List[PermissionSchema])
async def read_permissions(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user = Depends(AuthManager.get_current_active_user)
):
    """Obtener lista de permisos"""
    permissions = db.query(Permission).offset(skip).limit(limit).all()
    return permissions