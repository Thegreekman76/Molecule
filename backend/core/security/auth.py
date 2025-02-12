# core/security/auth.py
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session, relationship
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from core.database.base import Base
from core.database.database import get_db
from core.security.roles import user_roles, Role

# Configuración de seguridad
SECRET_KEY = "your-secret-key"  # Cambiar en producción
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Configuración de Password Context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

# Modelos Pydantic
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
    scopes: List[str] = []

class UserBase(BaseModel):
    username: str
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    is_active: bool = True
    is_superuser: bool = False

class UserCreate(UserBase):
    password: str

class UserUpdate(UserBase):
    password: Optional[str] = None

class User(UserBase):
    id: int

    class Config:
        from_attributes = True

# Modelo SQLAlchemy para Usuario
class UserModel(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True, nullable=True)
    full_name = Column(String, nullable=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)

    # Relación con roles
    roles = relationship("Role", secondary=user_roles, back_populates="users")

    def verify_password(self, plain_password: str) -> bool:
        """Verifica si la contraseña coincide con el hash"""
        return pwd_context.verify(plain_password, self.hashed_password)

# Funciones de autenticación
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica si la contraseña coincide con el hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Genera un hash para la contraseña"""
    return pwd_context.hash(password)

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Crea un token JWT"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Funciones de base de datos
def get_user_by_username(db: Session, username: str) -> Optional[UserModel]:
    """Obtiene un usuario por su username"""
    return db.query(UserModel).filter(UserModel.username == username).first()

def authenticate_user(db: Session, username: str, password: str) -> Optional[UserModel]:
    """Autentica un usuario por username y password"""
    user = get_user_by_username(db, username)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user

def create_user(db: Session, user: UserCreate) -> UserModel:
    """Crea un nuevo usuario"""
    hashed_password = get_password_hash(user.password)
    db_user = UserModel(
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        hashed_password=hashed_password,
        is_active=user.is_active,
        is_superuser=user.is_superuser
    )
    db.add(db_user)
    try:
        db.commit()
        db.refresh(db_user)
        return db_user
    except Exception as e:
        db.rollback()
        raise e

def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[UserModel]:
    """Obtiene una lista de usuarios"""
    return db.query(UserModel).offset(skip).limit(limit).all()

# Dependencias de FastAPI
async def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> UserModel:
    """Obtiene el usuario actual desde el token JWT"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception

    user = get_user_by_username(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(
    current_user: UserModel = Depends(get_current_user)
) -> UserModel:
    """Verifica si el usuario actual está activo"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

async def get_current_admin_user(
    current_user: UserModel = Depends(get_current_active_user),
) -> UserModel:
    """Verifica si el usuario actual es administrador"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough privileges",
        )
    return current_user