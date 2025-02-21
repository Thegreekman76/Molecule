from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class UsersBase(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    full_name: Optional[str] = None
    hashed_password: Optional[str] = None
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None

    model_config = {
        "json_encoders": {
            datetime: lambda v: v.isoformat() if v else None
        }
    }

class UsersCreate(UsersBase):
    pass

class UsersUpdate(UsersBase):
    username: Optional[str] = None
    email: Optional[str] = None
    full_name: Optional[str] = None
    hashed_password: Optional[str] = None
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None

class UsersInDB(UsersBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
