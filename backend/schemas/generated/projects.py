from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ProjectsBase(BaseModel):
    description: Optional[str]
    start_date: Optional[datetime]
    end_date: Optional[datetime]

class ProjectsCreate(ProjectsBase):
    pass

class ProjectsUpdate(ProjectsBase):
    pass

class ProjectsInDB(ProjectsBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True