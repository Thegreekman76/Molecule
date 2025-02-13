from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class UsersBase(BaseModel):
    username: Optional[str]
    email: Optional[str]
    full_name: Optional[str]
    hashed_password: Optional[str]
    is_active: Optional[bool]
    is_superuser: Optional[bool]

class UsersCreate(UsersBase):
    pass

class UsersUpdate(UsersBase):
    pass

class UsersInDB(UsersBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True