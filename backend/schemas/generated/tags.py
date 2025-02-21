from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class TagsBase(BaseModel):
    name: str
    color: str = Field(default='#6B7280')
    description: Optional[str] = None

    model_config = {
        "json_encoders": {
            datetime: lambda v: v.isoformat() if v else None
        }
    }

class TagsCreate(TagsBase):
    pass

class TagsUpdate(TagsBase):
    name: Optional[str] = None
    color: Optional[str] = None
    description: Optional[str] = None

class TagsInDB(TagsBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
