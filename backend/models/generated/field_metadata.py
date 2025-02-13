from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship
from core.database.base import Base


class FieldMetadata(Base):
    """Model for table field_metadata"""
    __tablename__ = 'field_metadata'

    id = Column(Integer, nullable=False, default=nextval('"public".field_metadata_id_seq'::regclass))
    table_id = Column(ForeignKey('table_metadata.id'))
    name = Column(String)
    display_name = Column(String)
    field_type = Column(String)
    length = Column(Integer)
    is_nullable = Column(Boolean)
    is_unique = Column(Boolean)
    default_value = Column(String)
    created_at = Column(DateTime, default=now())
    updated_at = Column(DateTime)
    ui_settings = Column(String)
    validation_rules = Column(String)
    table_metadata = relationship('TableMetadata')