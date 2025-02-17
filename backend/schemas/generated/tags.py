from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class TagsBase(BaseModel):

class TagsCreate(TagsBase):
    pass

class TagsUpdate(TagsBase):
    pass

class TagsInDB(TagsBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True