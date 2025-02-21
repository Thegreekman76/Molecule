# backend/core/generator/model_generator.py

from typing import Dict, List, Optional, Any
from sqlalchemy import MetaData, inspect, Table, text
from sqlalchemy.engine import Engine
from sqlalchemy.sql.type_api import TypeEngine
from dataclasses import dataclass
import logging
from core.database.database import engine

logger = logging.getLogger(__name__)

# Tablas del sistema que necesitan importación especial
SYSTEM_MODELS = {
    'table_metadata': ('TableMetadata', 'core.metadata.models'),
    'field_metadata': ('FieldMetadata', 'core.metadata.models'),
    'relationship_metadata': ('RelationshipMetadata', 'core.metadata.models'),
    'ui_templates': ('UITemplate', 'core.metadata.models'),
    'users': ('UserModel', 'core.security.auth'),
    'roles': ('Role', 'core.security.roles'),
    'permissions': ('Permission', 'core.security.roles'),
    'user_roles': ('UserRoles', 'core.metadata.models')
}

@dataclass
class ColumnInfo:
    name: str
    type: str
    nullable: bool
    primary_key: bool
    foreign_key: Optional[str]
    default: Any
    unique: bool
    comment: Optional[str]

@dataclass
class TableInfo:
    name: str
    schema: str
    columns: List[ColumnInfo]
    relationships: List[Dict[str, Any]]

class ModelGenerator:
    def __init__(self, engine: Engine):
        self.engine = engine
        self.metadata = MetaData()
        self.inspector = inspect(engine)
        logger.info("ModelGenerator initialized")
    
    def _generate_class_name(self, table_name: str) -> str:
        """Genera un nombre de clase a partir del nombre de la tabla"""
        return ''.join(word.capitalize() for word in table_name.split('_'))

    def get_tables(self, schema: str = 'public') -> List[str]:
        """Obtiene lista de tablas en el esquema especificado"""
        try:
            tables = self.inspector.get_table_names(schema=schema)
            logger.info(f"Found {len(tables)} tables in schema '{schema}'")
            return tables
        except Exception as e:
            logger.error(f"Error getting tables: {str(e)}")
            raise

    def get_table_info(self, table_name: str, schema: str = 'public') -> TableInfo:
        """Obtiene información detallada de una tabla"""
        try:
            columns = []
            relationships = []

            # Obtener información de columnas
            for col in self.inspector.get_columns(table_name, schema):
                foreign_key = None
                
                # Verificar si es foreign key
                for fk in self.inspector.get_foreign_keys(table_name, schema):
                    if col['name'] in fk['constrained_columns']:
                        foreign_key = f"{fk['referred_table']}.{fk['referred_columns'][0]}"
                        relationships.append({
                            'type': 'many_to_one',
                            'target_table': fk['referred_table'],
                            'local_column': col['name'],
                            'remote_column': fk['referred_columns'][0]
                        })

                # Procesar el valor por defecto si existe
                default_value = None
                if col.get('default') is not None:
                    default_value = self._process_default_value(col['default'])

                column = ColumnInfo(
                    name=col['name'],
                    type=str(col['type']),
                    nullable=col['nullable'],
                    primary_key=col.get('primary_key', False),
                    foreign_key=foreign_key,
                    default=default_value,
                    unique=any(col['name'] in u['column_names'] 
                             for u in self.inspector.get_unique_constraints(table_name, schema)),
                    comment=col.get('comment')
                )
                columns.append(column)

            logger.info(f"Analyzed table '{table_name}' structure")
            return TableInfo(
                name=table_name,
                schema=schema,
                columns=columns,
                relationships=relationships
            )
        except Exception as e:
            logger.error(f"Error analyzing table '{table_name}': {str(e)}")
            raise

    def _process_default_value(self, default: str) -> str:
        """Procesa y limpia valores por defecto de PostgreSQL"""
        if default is None:
            return None

        # Convertir a string para manipulación
        default_str = str(default)

        # Casos especiales de PostgreSQL
        if "nextval" in default_str:
            return None  # Ignoramos secuencias, se manejan automáticamente
        if "::regclass" in default_str:
            return None  # Ignoramos referencias a regclass
        if default_str.startswith("'") and default_str.endswith("'"):
            # Valores string literales
            return default_str
        if default_str.upper() in ['TRUE', 'FALSE']:
            # Booleanos
            return default_str.lower()
        if default_str.upper() in ['CURRENT_TIMESTAMP', 'NOW()', 'CURRENT_DATE']:
            # Timestamps
            return "func.now()"  # Cambiado de "now()" a "func.now()"
        if default_str.upper() == 'NULL':
            return None

        return default_str

    def generate_sqlalchemy_model(self, table_info: TableInfo) -> str:
        """Genera código del modelo SQLAlchemy desde los metadatos de tabla"""
        try:
            model_name = self._generate_class_name(table_info.name)
            
            # Imports necesarios
            imports = [
                "from sqlalchemy import Column, JSON, Integer, String, ForeignKey, Boolean, DateTime, Text, Float, Numeric, func, text",
                "from sqlalchemy.dialects.postgresql import JSONB",
                "from sqlalchemy.orm import relationship, Mapped",
                "from typing import Optional, List",
                "from datetime import datetime",
                "from core.database.base import Base",
                ""
            ]

            # Si es un modelo del sistema, usar un enfoque diferente
            if table_info.name in SYSTEM_MODELS:
                class_name, module_path = SYSTEM_MODELS[table_info.name]
                imports.append(f"from {module_path} import {class_name}")
                imports.append("")
                code = [
                    f"class {model_name}({class_name}):",
                    f'    """Model for table {table_info.name}"""',
                    "    __table_args__ = {'extend_existing': True}",
                    ""
                ]
                return '\n'.join(imports + code)

            # Código para tablas regulares
            code = [
                f"class {model_name}(Base):",
                f'    """Model for table {table_info.name}"""',
                f"    __tablename__ = '{table_info.name}'",
                "    __table_args__ = {'extend_existing': True}",
                ""
            ]

            # Obtener información de las columnas directamente de la base de datos
            with self.engine.connect() as conn:
                result = conn.execute(text(f"""
                    SELECT column_name, data_type, is_nullable, 
                        column_default, character_maximum_length
                    FROM information_schema.columns 
                    WHERE table_name = '{table_info.name}'
                    ORDER BY ordinal_position
                """))
                
                for row in result:
                    column_name = row[0]
                    data_type = row[1]
                    is_nullable = row[2] == 'YES'
                    default_value = row[3]
                    max_length = row[4]
                    
                    # Preparar argumentos
                    args = []
                    
                    # Determinar tipo SQLAlchemy
                    sa_type = self._map_to_sqlalchemy_type(data_type)
                    
                    # Agregar longitud para strings si es aplicable
                    if max_length is not None and sa_type == "String":
                        args.append(f"{sa_type}({max_length})")
                    else:
                        args.append(sa_type)
                    
                    # Primary key para columna id
                    if column_name == 'id':
                        args.append("primary_key=True")
                        # No añadir un valor por defecto para id, SQLAlchemy lo gestiona
                    elif not is_nullable:  # No incluir nullable=False para primary keys
                        args.append("nullable=False")
                    
                    # Procesar valor por defecto
                    if default_value is not None and column_name != 'id':  # Ignorar defaults para primary keys
                        default_str = str(default_value)
                        
                        # Manejar secuencias de PostgreSQL
                        if 'nextval' in default_str:
                            # Para ID, mejor dejar que SQLAlchemy lo maneje automáticamente
                            pass
                        # Limpiar sintaxis PostgreSQL
                        elif '::' in default_str:
                            default_str = default_str.split('::')[0]
                            
                            # Valores específicos
                            if default_str.upper() in ['CURRENT_TIMESTAMP', 'NOW()', 'CURRENT_DATE']:
                                if column_name == 'updated_at':
                                    args.append("server_default=func.now()")
                                    args.append("onupdate=func.now()")
                                else:
                                    args.append("server_default=func.now()")
                            elif default_str.startswith("'") and default_str.endswith("'"):
                                # Limpiar comillas para strings
                                clean_value = default_str.strip("'")
                                args.append(f"default='{clean_value}'")
                            else:
                                # Usar server_default con text() para otros valores literales SQL
                                args.append(f"server_default=text('{default_str}')")
                        else:
                            # Valores específicos
                            if default_str.upper() in ['CURRENT_TIMESTAMP', 'NOW()', 'CURRENT_DATE']:
                                if column_name == 'updated_at':
                                    args.append("server_default=func.now()")
                                    args.append("onupdate=func.now()")
                                else:
                                    args.append("server_default=func.now()")
                            elif default_str.startswith("'") and default_str.endswith("'"):
                                # Limpiar comillas para strings
                                clean_value = default_str.strip("'")
                                args.append(f"default='{clean_value}'")
                            else:
                                # Para valores numéricos o booleanos
                                args.append(f"default={default_str}")
                    
                    # Generar código de la columna
                    col_def = f"{column_name} = Column({', '.join(args)})"
                    code.append(f"    {col_def}")
            
            # Retornar código completo
            return '\n'.join(imports + code)
            
        except Exception as e:
            logger.error(f"Error generando modelo SQLAlchemy: {str(e)}")
            raise
    
    def _generate_relationship_definition(self, rel: Dict) -> Optional[str]:
        """Genera la definición de una relación"""
        try:
            target_model = self._generate_class_name(rel['target_table'])
            rel_type = rel['type'].lower()
            
            args = [f"'{target_model}'"]
            if rel_type in ['one_to_many', 'many_to_one']:
                args.append("back_populates=None")
                args.append(f"uselist={'True' if rel_type == 'one_to_many' else 'False'}")
            
            return f"{rel['target_table']} = relationship({', '.join(args)})"

        except Exception as e:
            logger.error(f"Error en _generate_relationship_definition: {str(e)}")
            return None
        
    def _generate_column_definition(self, col: ColumnInfo) -> Optional[str]:
        """Genera la definición de una columna"""
        try:
            args = []

            # Tipo base de la columna
            if col.foreign_key:
                args.append(f"ForeignKey('{col.foreign_key}')")
            else:
                col_type = self._map_to_sqlalchemy_type(col.type)
                if col.length and col_type == "String":
                    args.append(f"String({col.length})")
                else:
                    args.append(col_type)

            # Argumentos adicionales
            if not col.nullable:
                args.append("nullable=False")
            if col.unique:
                args.append("unique=True")

            # Valor por defecto
            if col.default is not None:
                default_value = str(col.default)
                # Limpiar sintaxis PostgreSQL
                if '::' in default_value:
                    default_value = default_value.split('::')[0]

                if default_value.upper() in ['CURRENT_TIMESTAMP', 'NOW()', 'CURRENT_DATE']:
                    args.append("server_default=func.now()")
                elif default_value.startswith("'") and default_value.endswith("'"):
                    args.append(f"server_default=text({default_value})")
                else:
                    args.append(f"default={default_value}")

            return f"{col.name} = Column({', '.join(args)})"

        except Exception as e:
            logger.error(f"Error en _generate_column_definition para {col.name}: {str(e)}")
            return None
        
    def _generate_column_code(self, column: ColumnInfo) -> Optional[str]:
        """Genera código para una columna SQLAlchemy"""
        try:
            args = []
            
            # Tipo de la columna
            if column.foreign_key:
                type_str = f"ForeignKey('{column.foreign_key}')"
            else:
                type_str = self._map_to_sqlalchemy_type(column.type)
            
            # Argumentos adicionales
            if not column.nullable:
                args.append("nullable=False")
            if column.unique:
                args.append("unique=True")
                
            # Manejo especial de valores por defecto
            if column.default:
                # Limpiamos cualquier tipo de casting de PostgreSQL
                default_value = column.default
                if '::' in default_value:
                    default_value = default_value.split('::')[0]
                
                # Si es un literal de string, lo mantenemos como está
                if default_value.startswith("'") and default_value.endswith("'"):
                    args.append(f"default={default_value}")
                # Si es una función como CURRENT_TIMESTAMP
                elif default_value.upper() in ['CURRENT_TIMESTAMP', 'NOW()', 'CURRENT_DATE']:
                    args.append("server_default=func.now()")
                # Para otros valores
                else:
                    args.append(f"default={default_value}")
            
            args_str = ", ".join([type_str] + args)
            return f"{column.name} = Column({args_str})"

        except Exception as e:
            logger.error(f"Error generating column code for {column.name}: {str(e)}")
            return None

    def _map_to_sqlalchemy_type(self, db_type: str) -> str:
        """Mapea tipos de base de datos a tipos SQLAlchemy"""
        db_type_lower = db_type.lower()
        
        type_mapping = {
            'integer': 'Integer',
            'bigint': 'Integer',
            'smallint': 'Integer',
            'int': 'Integer',
            'character varying': 'String',
            'varchar': 'String',
            'character': 'String',
            'text': 'Text',
            'boolean': 'Boolean',
            'timestamp': 'DateTime',
            'timestamp without time zone': 'DateTime',
            'timestamp with time zone': 'DateTime',
            'date': 'Date',
            'time': 'Time',
            'numeric': 'Numeric',
            'decimal': 'Numeric',
            'real': 'Float',
            'double precision': 'Float',
            'json': 'JSON',
            'jsonb': 'JSONB'
        }
        
        return type_mapping.get(db_type_lower, 'String')

    def generate_pydantic_schema(self, table_info: TableInfo) -> str:
        """Genera código del schema Pydantic"""
        try:
            model_name = self._generate_class_name(table_info.name)
            
            # Imports necesarios
            imports = [
                "from pydantic import BaseModel, Field",
                "from typing import Optional",
                "from datetime import datetime",
                ""
            ]

            # Detectar si hay campos datetime
            has_datetime_fields = any(
                'timestamp' in col.type.lower() or 'date' in col.type.lower() 
                for col in table_info.columns
            )
            
            # Schema Base
            code = [f"class {model_name}Base(BaseModel):"]
            
            # Generar campos
            for col in table_info.columns:
                if col.name not in ['id', 'created_at', 'updated_at']:
                    # Mapear tipo
                    field_type = self._map_to_pydantic_type(col.type)
                    is_nullable = col.nullable
                    
                    # Generar definición del campo
                    if is_nullable:
                        field_def = f"{col.name}: Optional[{field_type}] = None"
                    elif col.default is not None:
                        # Procesar valor por defecto
                        default_value = str(col.default)
                        
                        # Limpiar sintaxis PostgreSQL
                        if '::' in default_value:
                            default_value = default_value.split('::')[0]
                        
                        # Valores específicos según tipo
                        if field_type == 'datetime':
                            field_def = f"{col.name}: {field_type}"
                        elif default_value.startswith("'") and default_value.endswith("'"):
                            clean_value = default_value.strip("'")
                            field_def = f"{col.name}: {field_type} = Field(default='{clean_value}')"
                        else:
                            field_def = f"{col.name}: {field_type} = {default_value}"
                    else:
                        field_def = f"{col.name}: {field_type}"
                    
                    code.append(f"    {field_def}")
            
            # Agregar configuración para serializar datetime si es necesario
            if has_datetime_fields:
                code.append("")
                code.append("    model_config = {")
                code.append("        \"json_encoders\": {")
                code.append("            datetime: lambda v: v.isoformat() if v else None")
                code.append("        }")
                code.append("    }")
            
            code.append("")
            
            # Schema Create
            code.extend([
                f"class {model_name}Create({model_name}Base):",
                "    pass",
                ""
            ])
            
            # Schema Update
            update_code = [f"class {model_name}Update({model_name}Base):"]
            
            # Campos opcionales para Update
            for col in table_info.columns:
                if col.name not in ['id', 'created_at', 'updated_at']:
                    field_type = self._map_to_pydantic_type(col.type)
                    update_code.append(f"    {col.name}: Optional[{field_type}] = None")
            
            code.extend(update_code)
            code.append("")
            
            # Schema InDB
            code.extend([
                f"class {model_name}InDB({model_name}Base):",
                "    id: int",
                "    created_at: datetime",
                "    updated_at: Optional[datetime] = None",
                "",
                "    class Config:",
                "        from_attributes = True",
                ""
            ])
            
            return '\n'.join(imports + code)
            
        except Exception as e:
            logger.error(f"Error generando schema Pydantic: {str(e)}")
            raise

    def _generate_pydantic_field(self, column: ColumnInfo) -> Optional[str]:
        """Genera código para un campo Pydantic"""
        try:
            type_str = self._map_to_pydantic_type(column.type)
            if column.nullable:
                type_str = f"Optional[{type_str}]"
            
            field_args = []
            if column.default is not None and column.default != "func.now()":
                field_args.append(f"default={column.default}")
            
            field_str = f"Field({', '.join(field_args)})" if field_args else ""
            return f"{column.name}: {type_str}" + (f" = {field_str}" if field_str else "")

        except Exception as e:
            logger.error(f"Error generating Pydantic field for {column.name}: {str(e)}")
            return None

    def _map_to_pydantic_type(self, db_type: str) -> str:
        """Mapea tipos de base de datos a tipos Python/Pydantic"""
        db_type_lower = db_type.lower()
        
        # Mapeo de tipos
        type_mapping = {
            'integer': 'int',
            'bigint': 'int',
            'smallint': 'int',
            'int': 'int',
            'character varying': 'str',
            'varchar': 'str',
            'character': 'str',
            'text': 'str',
            'boolean': 'bool',
            'timestamp': 'datetime',
            'timestamp without time zone': 'datetime',
            'timestamp with time zone': 'datetime',
            'date': 'datetime',
            'time': 'datetime',
            'numeric': 'float',
            'decimal': 'float',
            'real': 'float',
            'double precision': 'float',
            'json': 'dict',
            'jsonb': 'dict',
        }
        
        # Tipos con parámetros
        if '(' in db_type_lower:
            base_type = db_type_lower.split('(')[0].strip()
            return type_mapping.get(base_type, 'str')
            
        return type_mapping.get(db_type_lower, 'str')

    def _map_simple_type(self, base_type: str) -> str:
        """Mapea un tipo simple de DB a Python"""
        type_mapping = {
            'integer': 'int',
            'bigint': 'int',
            'smallint': 'int',
            'character varying': 'str',
            'varchar': 'str',
            'character': 'str',
            'text': 'str',
            'boolean': 'bool',
            'timestamp': 'datetime',  # Usar datetime, no str
            'timestamp without time zone': 'datetime',  # Usar datetime, no str
            'timestamp with time zone': 'datetime',  # Usar datetime, no str
            'date': 'date',
            'time': 'time',
            'numeric': 'float',
            'decimal': 'float',
            'real': 'float',
            'double precision': 'float',
            'json': 'dict',
            'jsonb': 'dict',
        }
        
        return type_mapping.get(base_type, 'str')