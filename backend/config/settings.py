# backend\config\settings.py
from typing import Any, Dict, List
from pydantic import BaseModel, field_validator
import os
from functools import lru_cache
import logging.config

class Settings(BaseModel):
    # Server Config
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    
    # Project Info
    PROJECT_NAME: str = "Molecule Framework"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    
    # Database
    DATABASE_URL: str = "postgresql://admin:secret@localhost:5434/molecule_db"
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_TIMEOUT: int = 30
    
    # Security
    SECRET_KEY: str = "your-secret-key-here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 días
    
    # CORS Settings
    BACKEND_CORS_ORIGINS: List[str] = ["*"]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: List[str] = ["*"]
    CORS_ALLOW_HEADERS: List[str] = ["*"]
    
    # Cache Config
    CACHE_ENABLED: bool = True
    CACHE_EXPIRE_MINUTES: int = 15
    CACHE_TYPE: str = "memory"  # memory o redis
    
    # Logging Settings
    LOG_LEVEL: str = "DEBUG"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_FILE: str = "logs/molecule.log"

    def configure_logging(self) -> None:
        """Configura el sistema de logging"""
        # Crear directorio de logs si no existe
        os.makedirs("logs", exist_ok=True)

        config = {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": self.LOG_FORMAT,
                    "datefmt": "%Y-%m-%d %H:%M:%S",
                },
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "default",
                    "stream": "ext://sys.stdout",
                },
                "file": {
                    "class": "logging.FileHandler",
                    "formatter": "default",
                    "filename": self.LOG_FILE,
                    "mode": "a",
                    "encoding": "utf-8",
                },
            },
            "loggers": {
                "": {  # Root logger
                    "handlers": ["console", "file"],
                    "level": self.LOG_LEVEL,
                },
                "uvicorn": {
                    "handlers": ["console", "file"],
                    "level": self.LOG_LEVEL,
                },
                "sqlalchemy.engine": {
                    "handlers": ["console", "file"],
                    "level": self.LOG_LEVEL if self.DEBUG else "WARNING",
                    "propagate": False,
                },
            },
        }
        
        logging.config.dictConfig(config)

    @field_validator("DATABASE_URL")
    def validate_database_url(cls, v: str) -> str:
        if "postgresql://" not in v:
            DB_USER = os.getenv("DB_USER", "admin")
            DB_PASS = os.getenv("DB_PASS", "secret")
            DB_HOST = os.getenv("DB_HOST", "localhost")
            DB_PORT = os.getenv("DB_PORT", "5434")
            DB_NAME = os.getenv("DB_NAME", "molecule_db")
            return f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        return v

    def get_db_pool_settings(self) -> Dict[str, Any]:
        return {
            "pool_size": self.DB_POOL_SIZE,
            "max_overflow": self.DB_MAX_OVERFLOW,
            "pool_timeout": self.DB_POOL_TIMEOUT
        }

    class Config:
        case_sensitive = True
        extra = "allow"

settings = Settings()
# Configurar logging al inicializar settings
settings.configure_logging()