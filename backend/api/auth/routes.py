# api/auth/routes.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Any, List
from datetime import timedelta

from core.database.database import get_db
from core.security.auth import (
    Token,
    User,
    UserCreate,
    authenticate_user,
    create_access_token,
    get_current_active_user,
    get_current_admin_user,
    create_user,
    get_user_by_username,
    get_users,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

router = APIRouter()

@router.post("/login", response_model=Token)
async def login_for_access_token(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """Login para obtener token de acceso"""
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    # Incluir roles y permisos en el token
    access_token = create_access_token(
        data={
            "sub": user.username,
            "scopes": [role.name for role in user.roles] if user.roles else [],
            "is_superuser": user.is_superuser
        },
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/register", response_model=User)
async def register(
    *,
    db: Session = Depends(get_db),
    user_in: UserCreate,
) -> Any:
    """Registrar nuevo usuario"""
    user = get_user_by_username(db, username=user_in.username)
    if user:
        raise HTTPException(
            status_code=400,
            detail="El usuario ya existe en el sistema."
        )
    user = create_user(db, user_in)
    return user

@router.get("/users/me", response_model=User)
async def read_current_user(
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Obtener usuario actual"""
    return current_user

@router.get("/users", response_model=List[User])
async def read_users(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_admin_user),
) -> Any:
    """Obtener lista de usuarios (solo admin)"""
    users = get_users(db, skip=skip, limit=limit)
    return users