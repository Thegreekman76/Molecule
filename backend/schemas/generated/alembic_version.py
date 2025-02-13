from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class AlembicVersionBase(BaseModel):
    version_num: str

class AlembicVersionCreate(AlembicVersionBase):
    pass

class AlembicVersionUpdate(AlembicVersionBase):
    pass

class AlembicVersionInDB(AlembicVersionBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True