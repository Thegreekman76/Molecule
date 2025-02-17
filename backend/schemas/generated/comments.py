from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class CommentsBase(BaseModel):
    content: str
    author_id: int
    issue_id: int

class CommentsCreate(CommentsBase):
    pass

class CommentsUpdate(CommentsBase):
    pass

class CommentsInDB(CommentsBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True