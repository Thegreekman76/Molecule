from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class TableMetadataBase(BaseModel):
    name: Optional[str]
    display_name: Optional[str]
    description: Optional[str]
    is_visible: Optional[bool]
    ui_settings: Optional[str]
    db_schema: Optional[str]

class TableMetadataCreate(TableMetadataBase):
    pass

class TableMetadataUpdate(TableMetadataBase):
    pass

class TableMetadataInDB(TableMetadataBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True