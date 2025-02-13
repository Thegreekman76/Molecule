from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship
from core.database.base import Base


class RelationshipMetadata(Base):
    """Model for table relationship_metadata"""
    __tablename__ = 'relationship_metadata'

    id = Column(Integer, nullable=False, default=nextval('"public".relationship_metadata_id_seq'::regclass))
    source_table_id = Column(ForeignKey('table_metadata.id'))
    target_table_id = Column(ForeignKey('table_metadata.id'))
    relationship_type = Column(String)
    source_field = Column(String)
    target_field = Column(String)
    created_at = Column(DateTime, default=now())
    updated_at = Column(DateTime)
    table_metadata = relationship('TableMetadata')
    table_metadata = relationship('TableMetadata')