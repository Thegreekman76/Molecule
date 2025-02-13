from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class RelationshipMetadataBase(BaseModel):
    source_table_id: Optional[int]
    target_table_id: Optional[int]
    relationship_type: Optional[str]
    source_field: Optional[str]
    target_field: Optional[str]

class RelationshipMetadataCreate(RelationshipMetadataBase):
    pass

class RelationshipMetadataUpdate(RelationshipMetadataBase):
    pass

class RelationshipMetadataInDB(RelationshipMetadataBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True