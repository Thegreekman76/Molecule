from sqlalchemy import Column, JSON, Integer, String, ForeignKey, Boolean, DateTime, Text, Float, Numeric, func, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship, Mapped
from typing import Optional, List
from datetime import datetime
from core.database.base import Base

from core.security.auth import UserModel

# Este modelo utiliza la definición de tabla de UserModel del sistema
# No necesitas redefinir este modelo, usa UserModel directamente
Users = UserModel  # Alias para mantener consistencia en nombres
