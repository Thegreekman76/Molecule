# schemas/base.py
from datetime import datetime
from typing import Optional, TypeVar, Generic
from pydantic import BaseModel, ConfigDict

ModelType = TypeVar("ModelType")

class BaseSchema(BaseModel):
    """Base schema for all models"""
    model_config = ConfigDict(from_attributes=True)

class BaseCreateSchema(BaseSchema):
    """Base schema for create operations"""
    pass

class BaseUpdateSchema(BaseSchema):
    """Base schema for update operations"""
    pass

class BaseInDBSchema(BaseSchema):
    """Base schema for database models"""
    id: int
    created_at: datetime
    updated_at: datetime

