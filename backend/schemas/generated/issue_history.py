from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class IssueHistoryBase(BaseModel):
    issue_id: int
    old_value: Optional[str]
    new_value: Optional[str]
    changed_by: int

class IssueHistoryCreate(IssueHistoryBase):
    pass

class IssueHistoryUpdate(IssueHistoryBase):
    pass

class IssueHistoryInDB(IssueHistoryBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True