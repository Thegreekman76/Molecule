from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class RolesBase(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None

    model_config = {
        "json_encoders": {
            datetime: lambda v: v.isoformat() if v else None
        }
    }

class RolesCreate(RolesBase):
    pass

class RolesUpdate(RolesBase):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None

class RolesInDB(RolesBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
