# config/settings.py
from typing import Any, Dict, List
from pydantic import BaseModel

class Settings(BaseModel):
    # Server Config
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Project Info
    PROJECT_NAME: str = "Molecule Framework"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    
    # Database
    DATABASE_URL: str = "postgresql://admin:secret@localhost:5434/molecule_db"
    
    # Security
    SECRET_KEY: str = "your-secret-key-here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

# Instancia global de configuración
settings = Settings()