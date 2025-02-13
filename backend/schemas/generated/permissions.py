from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class PermissionsBase(BaseModel):
    name: Optional[str]
    description: Optional[str]
    resource: Optional[str]
    action: Optional[str]

class PermissionsCreate(PermissionsBase):
    pass

class PermissionsUpdate(PermissionsBase):
    pass

class PermissionsInDB(PermissionsBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True