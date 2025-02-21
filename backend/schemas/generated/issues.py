from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class IssuesBase(BaseModel):
    title: str
    description: str
    status: str = Field(default='open')
    priority: str = Field(default='medium')
    type: str = Field(default='bug')
    assigned_to: Optional[int] = None
    due_date: Optional[datetime] = None
    estimated_hours: Optional[float] = None

    model_config = {
        "json_encoders": {
            datetime: lambda v: v.isoformat() if v else None
        }
    }

class IssuesCreate(IssuesBase):
    pass

class IssuesUpdate(IssuesBase):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    type: Optional[str] = None
    assigned_to: Optional[int] = None
    due_date: Optional[datetime] = None
    estimated_hours: Optional[float] = None

class IssuesInDB(IssuesBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
