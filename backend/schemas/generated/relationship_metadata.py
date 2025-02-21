from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class RelationshipMetadataBase(BaseModel):
    source_table_id: Optional[int] = None
    target_table_id: Optional[int] = None
    relationship_type: Optional[str] = None
    source_field: Optional[str] = None
    target_field: Optional[str] = None

    model_config = {
        "json_encoders": {
            datetime: lambda v: v.isoformat() if v else None
        }
    }

class RelationshipMetadataCreate(RelationshipMetadataBase):
    pass

class RelationshipMetadataUpdate(RelationshipMetadataBase):
    source_table_id: Optional[int] = None
    target_table_id: Optional[int] = None
    relationship_type: Optional[str] = None
    source_field: Optional[str] = None
    target_field: Optional[str] = None

class RelationshipMetadataInDB(RelationshipMetadataBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
