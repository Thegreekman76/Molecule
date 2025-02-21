from sqlalchemy import Column, JSON, Integer, String, ForeignKey, Boolean, DateTime, Text, Float, Numeric, func, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship, Mapped
from typing import Optional, List
from datetime import datetime
from core.database.base import Base

from core.metadata.models import UITemplate

# Este modelo utiliza la definición de tabla de UITemplate del sistema
# No necesitas redefinir este modelo, usa UITemplate directamente
UiTemplates = UITemplate  # Alias para mantener consistencia en nombres
