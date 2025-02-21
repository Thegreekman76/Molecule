from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class IssueHistoryBase(BaseModel):
    issue_id: int
    field_changed: str
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    changed_by: int

    model_config = {
        "json_encoders": {
            datetime: lambda v: v.isoformat() if v else None
        }
    }

class IssueHistoryCreate(IssueHistoryBase):
    pass

class IssueHistoryUpdate(IssueHistoryBase):
    issue_id: Optional[int] = None
    field_changed: Optional[str] = None
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    changed_by: Optional[int] = None

class IssueHistoryInDB(IssueHistoryBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
