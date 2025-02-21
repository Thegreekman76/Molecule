from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class UiTemplatesBase(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    template_type: Optional[str] = None
    configuration: Optional[dict] = None

    model_config = {
        "json_encoders": {
            datetime: lambda v: v.isoformat() if v else None
        }
    }

class UiTemplatesCreate(UiTemplatesBase):
    pass

class UiTemplatesUpdate(UiTemplatesBase):
    name: Optional[str] = None
    description: Optional[str] = None
    template_type: Optional[str] = None
    configuration: Optional[dict] = None

class UiTemplatesInDB(UiTemplatesBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
