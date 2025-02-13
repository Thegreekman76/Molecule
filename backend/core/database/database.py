# core/database/database.py
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from sqlalchemy.engine import Engine
from config.settings import get_settings, settings
from typing import Generator
import logging
import logging.config
import time

# Obtener settings
settings = get_settings()

# Configurar logging básico primero
logging.basicConfig(level=settings.LOG_LEVEL)
logger = logging.getLogger(__name__)

# Configurar logging avanzado si está disponible
try:
    logging.config.dictConfig(settings.get_logging_config())
except (ValueError, OSError) as e:
    logger.warning(f"No se pudo configurar el logging avanzado: {str(e)}")
    logger.warning("Usando configuración de logging básica")

# Crear el engine con configuración mejorada
engine = create_engine(
    settings.DATABASE_URL,
    poolclass=QueuePool,
    echo=settings.DEBUG,  # Esto activará el logging SQL
    **settings.get_db_pool_settings()
)

@event.listens_for(Engine, "before_cursor_execute")
def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    conn.info.setdefault('query_start_time', time.time())
    if settings.DEBUG:
        logger.debug("SQL Query: %s", statement)
        logger.debug("Parameters: %r", parameters)

@event.listens_for(Engine, "after_cursor_execute")
def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    total = time.time() - conn.info['query_start_time']
    if settings.DEBUG:
        logger.debug("Query Complete!")
        logger.debug("Total Time: %f", total)


# Crear sessionmaker
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False
)

def get_db() -> Generator[Session, None, None]:
    """Dependency para obtener sesión de DB"""
    if settings.DEBUG:
        logger.debug("Opening new database connection")
    
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        db.rollback()
        raise
    finally:
        if settings.DEBUG:
            logger.debug("Closing database connection")
        db.close()

def check_db_connection() -> bool:
    """Verificar conexión a la base de datos"""
    try:
        db = SessionLocal()
        db.execute("SELECT 1")
        logger.info("Database connection successful")
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {str(e)}")
        return False
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
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        raise