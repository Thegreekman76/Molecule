from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class UserRolesBase(BaseModel):
    user_id: int
    role_id: int

    model_config = {
        "json_encoders": {
            datetime: lambda v: v.isoformat() if v else None
        }
    }

class UserRolesCreate(UserRolesBase):
    pass

class UserRolesUpdate(UserRolesBase):
    user_id: Optional[int] = None
    role_id: Optional[int] = None

class UserRolesInDB(UserRolesBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
