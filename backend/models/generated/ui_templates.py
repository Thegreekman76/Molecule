from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship
from core.database.base import Base


class UiTemplates(Base):
    """Model for table ui_templates"""
    __tablename__ = 'ui_templates'

    id = Column(Integer, nullable=False, default=nextval('"public".ui_templates_id_seq'::regclass))
    name = Column(String, unique=True)
    description = Column(String)
    template_type = Column(String)
    configuration = Column(String)
    created_at = Column(DateTime, default=now())
    updated_at = Column(DateTime)