# api/metadata/crud.py
from typing import List, Optional
from sqlalchemy.orm import Session
from core.metadata.models import TableMetadata, FieldMetadata, RelationshipMetadata
from core.metadata.schema import (
    TableMetadataCreate,
    TableMetadataUpdate,
    FieldMetadataCreate,
    FieldMetadataUpdate,
    RelationshipMetadataCreate,
    RelationshipMetadataUpdate
)
from utils.helpers import CRUDHelper

class TableMetadataCRUD(CRUDHelper[TableMetadata, TableMetadataCreate, TableMetadataUpdate]):
    """CRUD operations for table metadata"""
    
    def get_by_name(self, db: Session, name: str) -> Optional[TableMetadata]:
        """Get table metadata by name"""
        return db.query(self.model).filter(self.model.name == name).first()

    def get_with_fields(self, db: Session, id: int) -> Optional[TableMetadata]:
        """Get table metadata with all fields"""
        return (
            db.query(self.model)
            .filter(self.model.id == id)
            .first()
        )

class FieldMetadataCRUD(CRUDHelper[FieldMetadata, FieldMetadataCreate, FieldMetadataUpdate]):
    """CRUD operations for field metadata"""
    
    def get_by_table(self, db: Session, table_id: int) -> List[FieldMetadata]:
        """Get all fields for a table"""
        return (
            db.query(self.model)
            .filter(self.model.table_id == table_id)
            .all()
        )

class RelationshipMetadataCRUD(
    CRUDHelper[RelationshipMetadata, RelationshipMetadataCreate, RelationshipMetadataUpdate]
):
    """CRUD operations for relationship metadata"""
    
    def get_by_source_table(self, db: Session, table_id: int) -> List[RelationshipMetadata]:
        """Get all relationships where table is source"""
        return (
            db.query(self.model)
            .filter(self.model.source_table_id == table_id)
            .all()
        )

    def get_by_target_table(self, db: Session, table_id: int) -> List[RelationshipMetadata]:
        """Get all relationships where table is target"""
        return (
            db.query(self.model)
            .filter(self.model.target_table_id == table_id)
            .all()
        )

table_metadata = TableMetadataCRUD(TableMetadata)
field_metadata = FieldMetadataCRUD(FieldMetadata)
relationship_metadata = RelationshipMetadataCRUD(RelationshipMetadata)