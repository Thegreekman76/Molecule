from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class UiTemplatesBase(BaseModel):
    name: Optional[str]
    description: Optional[str]
    template_type: Optional[str]
    configuration: Optional[str]

class UiTemplatesCreate(UiTemplatesBase):
    pass

class UiTemplatesUpdate(UiTemplatesBase):
    pass

class UiTemplatesInDB(UiTemplatesBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True