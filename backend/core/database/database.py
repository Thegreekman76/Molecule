# core/database/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from config.settings import settings
from typing import Generator
import logging

# Configurar logging
logger = logging.getLogger(__name__)

# Crear el engine con pool de conexiones
engine = create_engine(
    settings.DATABASE_URL,
    poolclass=QueuePool,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_timeout=settings.DB_POOL_TIMEOUT,
    pool_pre_ping=True,  # Verificar conexiones antes de usarlas
    echo=False  # Set to True para ver queries SQL en logs
)

# Crear sessionmaker
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False
)

def get_db() -> Generator[Session, None, None]:
    """Dependency para obtener sesión de DB"""
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()

def init_db() -> None:
    """Inicializar la base de datos"""
    try:
        # Importar todos los modelos aquí
        from core.security.auth import UserModel
        from core.security.roles import Role, Permission
        from core.metadata.models import TableMetadata, FieldMetadata, RelationshipMetadata
        
        # Crear las tablas
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        raise

def check_db_connection() -> bool:
    """Verificar conexión a la base de datos"""
    try:
        db = SessionLocal()
        db.execute("SELECT 1")
        return True
    except Exception as e:
        logger.error(f"Database connection check failed: {str(e)}")
        return False
    finally:
        db.close()