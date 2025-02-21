from sqlalchemy import Column, JSON, Integer, String, ForeignKey, Boolean, DateTime, Text, Float, Numeric, func, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship, Mapped
from typing import Optional, List
from datetime import datetime
from core.database.base import Base

from core.metadata.models import RelationshipMetadata

class RelationshipMetadata(RelationshipMetadata):
    """Model for table relationship_metadata"""
    __table_args__ = {'extend_existing': True}
