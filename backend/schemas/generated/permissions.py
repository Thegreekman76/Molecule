from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class PermissionsBase(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    resource: Optional[str] = None
    action: Optional[str] = None

    model_config = {
        "json_encoders": {
            datetime: lambda v: v.isoformat() if v else None
        }
    }

class PermissionsCreate(PermissionsBase):
    pass

class PermissionsUpdate(PermissionsBase):
    name: Optional[str] = None
    description: Optional[str] = None
    resource: Optional[str] = None
    action: Optional[str] = None

class PermissionsInDB(PermissionsBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
