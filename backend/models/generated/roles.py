from sqlalchemy import Column, JSON, Integer, String, ForeignKey, Boolean, DateTime, Text, Float, Numeric, func, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship, Mapped
from typing import Optional, List
from datetime import datetime
from core.database.base import Base

from core.security.roles import Role

# Este modelo utiliza la definición de tabla de Role del sistema
# No necesitas redefinir este modelo, usa Role directamente
Roles = Role  # Alias para mantener consistencia en nombres
