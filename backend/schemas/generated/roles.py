from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class RolesBase(BaseModel):
    name: Optional[str]
    description: Optional[str]
    is_active: Optional[bool]

class RolesCreate(RolesBase):
    pass

class RolesUpdate(RolesBase):
    pass

class RolesInDB(RolesBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True