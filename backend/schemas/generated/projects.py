from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class ProjectsBase(BaseModel):
    name: str
    description: Optional[str] = None
    status: str = Field(default='active')
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

    model_config = {
        "json_encoders": {
            datetime: lambda v: v.isoformat() if v else None
        }
    }

class ProjectsCreate(ProjectsBase):
    pass

class ProjectsUpdate(ProjectsBase):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

class ProjectsInDB(ProjectsBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
