from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class FieldMetadataBase(BaseModel):
    table_id: Optional[int]
    name: Optional[str]
    display_name: Optional[str]
    field_type: Optional[str]
    length: Optional[int]
    is_nullable: Optional[bool]
    is_unique: Optional[bool]
    default_value: Optional[str]
    ui_settings: Optional[str]
    validation_rules: Optional[str]

class FieldMetadataCreate(FieldMetadataBase):
    pass

class FieldMetadataUpdate(FieldMetadataBase):
    pass

class FieldMetadataInDB(FieldMetadataBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True