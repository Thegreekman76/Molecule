# config/settings.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Any, Dict, Optional, List

class Settings(BaseSettings):
    # Configuración del Servidor
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Configuración Base
    PROJECT_NAME: str = "Molecule Framework"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    
    # Configuración de Base de Datos
    DATABASE_URL: str = "postgresql://admin:secret@localhost:5434/molecule_db"
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_TIMEOUT: int = 30
    
    # Configuración de Seguridad
    SECRET_KEY: str = "your-secret-key-here"  # Cambiar en producción
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 días
    
    # Configuración de CORS
    BACKEND_CORS_ORIGINS: List[str] = ["*"]
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # Configuración de Cache
    CACHE_ENABLED: bool = True
    CACHE_EXPIRE_MINUTES: int = 15
    
    # Logs
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        case_sensitive=True,
        extra='allow'  # Permitir campos extra
    )

# Instancia de configuración
settings = Settings()

# Configuraciones para diferentes ambientes
class DevSettings(Settings):
    model_config = SettingsConfigDict(env_file='.env.dev')

class ProdSettings(Settings):
    model_config = SettingsConfigDict(env_file='.env.prod')

class TestSettings(Settings):
    model_config = SettingsConfigDict(env_file='.env.test')