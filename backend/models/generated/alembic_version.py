from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship
from core.database.base import Base


class AlembicVersion(Base):
    """Model for table alembic_version"""
    __tablename__ = 'alembic_version'

    version_num = Column(String, nullable=False)