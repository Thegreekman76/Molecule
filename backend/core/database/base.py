# backend\core\database\base.py
from typing import Any
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, Integer, DateTime, text
from datetime import datetime
from sqlalchemy.orm import mapped_column

class Base(DeclarativeBase):
    """Base class for all database models"""
    
    @declared_attr
    def __tablename__(cls) -> str:
        """Generate __tablename__ automatically from class name"""
        return cls.__name__.lower()
    
    __table_args__ = {'extend_existing': True}
    
    # Columnas comunes para todos los modelos
    id = mapped_column(Integer, primary_key=True, index=True)
    created_at = mapped_column(
        DateTime, 
        nullable=False, 
        default=datetime.utcnow,
        server_default=text('CURRENT_TIMESTAMP')
    )
    updated_at = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        server_default=text('CURRENT_TIMESTAMP')
    )

    def dict(self) -> dict[str, Any]:
        """Convert model instance to dictionary"""
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }

    def update(self, **kwargs):
        """Update model instance with given kwargs"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)