from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class IssueTagsBase(BaseModel):
    issue_id: int
    tag_id: int

    model_config = {
        "json_encoders": {
            datetime: lambda v: v.isoformat() if v else None
        }
    }

class IssueTagsCreate(IssueTagsBase):
    pass

class IssueTagsUpdate(IssueTagsBase):
    issue_id: Optional[int] = None
    tag_id: Optional[int] = None

class IssueTagsInDB(IssueTagsBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
