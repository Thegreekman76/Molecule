from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class IssuesBase(BaseModel):
    description: str
    assigned_to: Optional[int]
    due_date: Optional[datetime]
    estimated_hours: Optional[str]

class IssuesCreate(IssuesBase):
    pass

class IssuesUpdate(IssuesBase):
    pass

class IssuesInDB(IssuesBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True