from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship
from core.database.base import Base


class TableMetadata(Base):
    """Model for table table_metadata"""
    __tablename__ = 'table_metadata'

    id = Column(Integer, nullable=False, default=nextval('"public".table_metadata_id_seq'::regclass))
    name = Column(String)
    display_name = Column(String)
    description = Column(String)
    is_visible = Column(Boolean)
    created_at = Column(DateTime, default=now())
    updated_at = Column(DateTime)
    ui_settings = Column(String)
    db_schema = Column(String)