from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class UserRolesBase(BaseModel):
    user_id: int
    role_id: int

class UserRolesCreate(UserRolesBase):
    pass

class UserRolesUpdate(UserRolesBase):
    pass

class UserRolesInDB(UserRolesBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True