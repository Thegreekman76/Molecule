# config/settings.py
from typing import Any, Dict, List
from pydantic import BaseModel, field_validator
import os
from functools import lru_cache

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
    DB_ECHO: bool = False  # SQL Echo for debugging
    
    # Security
    SECRET_KEY: str = "your-secret-key-here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 días
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["*"]
    
    # Cache Config
    CACHE_ENABLED: bool = True
    CACHE_EXPIRE_MINUTES: int = 15
    CACHE_TYPE: str = "memory"  # memory o redis
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    USE_FILE_LOGGING: bool = False

    @field_validator("DATABASE_URL")
    def validate_database_url(cls, v: str) -> str:
        """Validar y construir DATABASE_URL desde variables de entorno si es necesario"""
        if "postgresql://" not in v:
            # Construir desde variables de entorno
            DB_USER = os.getenv("DB_USER", "admin")
            DB_PASS = os.getenv("DB_PASS", "secret")
            DB_HOST = os.getenv("DB_HOST", "localhost")
            DB_PORT = os.getenv("DB_PORT", "5434")
            DB_NAME = os.getenv("DB_NAME", "molecule_db")
            
            return f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        return v

    @field_validator("BACKEND_CORS_ORIGINS")
    def validate_cors_origins(cls, v: List[str]) -> List[str]:
        """Validar y procesar orígenes CORS"""
        if v == ["*"]:
            return v
        return [origin.strip() for origin in v if origin.strip()]

    def get_db_pool_settings(self) -> Dict[str, Any]:
        """Obtener configuración del pool de base de datos"""
        return {
            "pool_size": self.DB_POOL_SIZE,
            "max_overflow": self.DB_MAX_OVERFLOW,
            "pool_timeout": self.DB_POOL_TIMEOUT,
            "echo": self.DB_ECHO
        }

    def get_logging_config(self) -> Dict[str, Any]:
        """Obtener configuración de logging"""
        config = {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": self.LOG_FORMAT
                }
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "default",
                    "level": self.LOG_LEVEL
                }
            },
            "root": {
                "level": self.LOG_LEVEL,
                "handlers": ["console"]
            }
        }

        return config

    class Config:
        case_sensitive = True
        extra = "allow"  # Permitir campos extra en la configuración

@lru_cache()
def get_settings() -> Settings:
    """Obtener instancia cacheada de settings"""
    return Settings()

# Instancia global de settings
settings = get_settings()