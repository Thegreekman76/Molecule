from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class IssueTagsBase(BaseModel):
    issue_id: int
    tag_id: int

class IssueTagsCreate(IssueTagsBase):
    pass

class IssueTagsUpdate(IssueTagsBase):
    pass

class IssueTagsInDB(IssueTagsBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True