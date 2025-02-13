from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class RolePermissionsBase(BaseModel):
    role_id: Optional[int]
    permission_id: Optional[int]

class RolePermissionsCreate(RolePermissionsBase):
    pass

class RolePermissionsUpdate(RolePermissionsBase):
    pass

class RolePermissionsInDB(RolePermissionsBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True