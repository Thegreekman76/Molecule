# backend/core/metadata/schema.py
from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Any
from datetime import datetime

class TableMetadataBase(BaseModel):
    name: str
    display_name: str
    description: Optional[str] = None
    db_schema: str = "public"  # Cambiado de 'schema' a 'db_schema'
    is_visible: bool = True
    ui_settings: Dict[str, Any] = Field(default_factory=dict)

class TableMetadataCreate(TableMetadataBase):
    pass

class TableMetadataUpdate(TableMetadataBase):
    name: Optional[str] = None
    display_name: Optional[str] = None

class TableMetadataInDB(TableMetadataBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class FieldMetadataBase(BaseModel):
    name: str
    display_name: str
    field_type: str
    length: Optional[int] = None
    is_nullable: bool = True
    is_unique: bool = False
    default_value: Optional[str] = None
    ui_settings: Dict[str, Any] = Field(default_factory=dict)
    validation_rules: Dict[str, Any] = Field(default_factory=dict)

class FieldMetadataCreate(FieldMetadataBase):
    table_id: int

class FieldMetadataUpdate(FieldMetadataBase):
    name: Optional[str] = None
    display_name: Optional[str] = None
    field_type: Optional[str] = None

class FieldMetadataInDB(FieldMetadataBase):
    id: int
    table_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class RelationshipMetadataBase(BaseModel):
    source_table_id: int
    target_table_id: int
    relationship_type: str
    source_field: str
    target_field: str

class RelationshipMetadataCreate(RelationshipMetadataBase):
    pass

class RelationshipMetadataUpdate(RelationshipMetadataBase):
    source_table_id: Optional[int] = None
    target_table_id: Optional[int] = None
    relationship_type: Optional[str] = None

class RelationshipMetadataInDB(RelationshipMetadataBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class UITemplateBase(BaseModel):
    name: str
    description: Optional[str] = None
    template_type: str
    configuration: Dict[str, Any]

class UITemplateCreate(UITemplateBase):
    pass

class UITemplateUpdate(UITemplateBase):
    name: Optional[str] = None
    template_type: Optional[str] = None
    configuration: Optional[Dict[str, Any]] = None

class UITemplateInDB(UITemplateBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True