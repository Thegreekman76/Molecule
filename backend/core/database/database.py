# core/database/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from config.settings import settings
from typing import Generator

# Crear el engine
engine = create_engine(
    settings.DATABASE_URL,
    pool_size=5,
    max_overflow=10
)

# Crear sessionmaker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Generator[Session, None, None]:
    """Dependency para obtener sesión de DB"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()