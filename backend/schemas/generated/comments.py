from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class CommentsBase(BaseModel):
    content: str
    author_id: int
    issue_id: int

    model_config = {
        "json_encoders": {
            datetime: lambda v: v.isoformat() if v else None
        }
    }

class CommentsCreate(CommentsBase):
    pass

class CommentsUpdate(CommentsBase):
    content: Optional[str] = None
    author_id: Optional[int] = None
    issue_id: Optional[int] = None

class CommentsInDB(CommentsBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
