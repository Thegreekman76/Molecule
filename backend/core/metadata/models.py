# backend/core/metadata/models.py
from sqlalchemy import Column, Integer, String, JSON, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from core.database.base import Base

class TableMetadata(Base):
    __tablename__ = "table_metadata"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    display_name = Column(String)
    description = Column(String, nullable=True)
    db_schema = Column(String, default="public")  # Cambiado de 'schema' a 'db_schema'
    is_visible = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Configuración UI
    ui_settings = Column(JSON, default={})
    
    # Relaciones
    fields = relationship("FieldMetadata", back_populates="table")
    
class FieldMetadata(Base):
    __tablename__ = "field_metadata"

    id = Column(Integer, primary_key=True, index=True)
    table_id = Column(Integer, ForeignKey("table_metadata.id"))
    name = Column(String)
    display_name = Column(String)
    field_type = Column(String)  # varchar, integer, etc.
    length = Column(Integer, nullable=True)
    is_nullable = Column(Boolean, default=True)
    is_unique = Column(Boolean, default=False)
    default_value = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Configuración UI
    ui_settings = Column(JSON, default={})
    validation_rules = Column(JSON, default={})
    
    # Relaciones
    table = relationship("TableMetadata", back_populates="fields")
    
class RelationshipMetadata(Base):
    __tablename__ = "relationship_metadata"

    id = Column(Integer, primary_key=True, index=True)
    source_table_id = Column(Integer, ForeignKey("table_metadata.id"))
    target_table_id = Column(Integer, ForeignKey("table_metadata.id"))
    relationship_type = Column(String)  # OneToOne, OneToMany, ManyToMany
    source_field = Column(String)
    target_field = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class UITemplate(Base):
    __tablename__ = "ui_templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    description = Column(String, nullable=True)
    template_type = Column(String)  # form, grid, master-detail
    configuration = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())