# core/database/database.py
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from sqlalchemy.engine import Engine
from config.settings import settings
from typing import Generator
import logging
import logging.config
import time
import os

# Asegurar que la carpeta logs existe
os.makedirs("logs", exist_ok=True)

# Configurar logging
logger = logging.getLogger(__name__)

logger.info("Initializing database engine...")
engine = create_engine(
    settings.DATABASE_URL,
    poolclass=QueuePool,
    echo=settings.DEBUG,
    **settings.get_db_pool_settings()
)
logger.info("Database engine initialized successfully")


# Event listeners para logging detallado de SQL
@event.listens_for(Engine, "before_cursor_execute")
def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    conn.info.setdefault('query_start_time', time.time())
    if settings.DEBUG:
        logger.debug("SQL Query Starting: %s", statement)
        logger.debug("Parameters: %r", parameters)

@event.listens_for(Engine, "after_cursor_execute")
def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    total = time.time() - conn.info['query_start_time']
    if settings.DEBUG:
        logger.debug("SQL Query Completed in %.3f seconds", total)

# Crear sessionmaker
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False
)
logger.info("Database session factory created")

def get_db() -> Generator[Session, None, None]:
    """Dependency para obtener sesión de DB"""
    if settings.DEBUG:
        logger.debug("Opening new database connection")
    
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database error occurred: {str(e)}", exc_info=True)
        db.rollback()
        raise
    finally:
        if settings.DEBUG:
            logger.debug("Closing database connection")
        db.close()

def check_db_connection() -> bool:
    """Verificar conexión a la base de datos"""
    try:
        logger.info("Checking database connection...")
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        logger.info("Database connection successful")
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {str(e)}", exc_info=True)
        return False
    finally:
        db.close()