from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class TableMetadataBase(BaseModel):
    name: Optional[str] = None
    display_name: Optional[str] = None
    description: Optional[str] = None
    is_visible: Optional[bool] = None
    ui_settings: Optional[dict] = None
    db_schema: Optional[str] = None

    model_config = {
        "json_encoders": {
            datetime: lambda v: v.isoformat() if v else None
        }
    }

class TableMetadataCreate(TableMetadataBase):
    pass

class TableMetadataUpdate(TableMetadataBase):
    name: Optional[str] = None
    display_name: Optional[str] = None
    description: Optional[str] = None
    is_visible: Optional[bool] = None
    ui_settings: Optional[dict] = None
    db_schema: Optional[str] = None

class TableMetadataInDB(TableMetadataBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
