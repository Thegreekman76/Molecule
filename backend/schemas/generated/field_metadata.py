from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class FieldMetadataBase(BaseModel):
    table_id: Optional[int] = None
    name: Optional[str] = None
    display_name: Optional[str] = None
    field_type: Optional[str] = None
    length: Optional[int] = None
    is_nullable: Optional[bool] = None
    is_unique: Optional[bool] = None
    default_value: Optional[str] = None
    ui_settings: Optional[dict] = None
    validation_rules: Optional[dict] = None

    model_config = {
        "json_encoders": {
            datetime: lambda v: v.isoformat() if v else None
        }
    }

class FieldMetadataCreate(FieldMetadataBase):
    pass

class FieldMetadataUpdate(FieldMetadataBase):
    table_id: Optional[int] = None
    name: Optional[str] = None
    display_name: Optional[str] = None
    field_type: Optional[str] = None
    length: Optional[int] = None
    is_nullable: Optional[bool] = None
    is_unique: Optional[bool] = None
    default_value: Optional[str] = None
    ui_settings: Optional[dict] = None
    validation_rules: Optional[dict] = None

class FieldMetadataInDB(FieldMetadataBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
