from sqlalchemy import Column, JSON, Integer, String, ForeignKey, Boolean, DateTime, Text, Float, Numeric, func, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship, Mapped
from typing import Optional, List
from datetime import datetime
from core.database.base import Base

from core.metadata.models import TableMetadata

# Este modelo utiliza la definición de tabla de TableMetadata del sistema
# No necesitas redefinir este modelo, usa TableMetadata directamente
TableMetadata = TableMetadata  # Alias para mantener consistencia en nombres
