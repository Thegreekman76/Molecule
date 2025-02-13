# core/generator/model_generator.py
from typing import Dict, List, Optional, Any
from sqlalchemy import MetaData, inspect, Table
from sqlalchemy.engine import Engine
from sqlalchemy.sql.type_api import TypeEngine
from dataclasses import dataclass
import logging
from core.database.database import engine

logger = logging.getLogger(__name__)

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

                column = ColumnInfo(
                    name=col['name'],
                    type=str(col['type']),
                    nullable=col['nullable'],
                    primary_key=col.get('primary_key', False),
                    foreign_key=foreign_key,
                    default=col.get('default'),
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

    def generate_sqlalchemy_model(self, table_info: TableInfo) -> str:
        """Genera código del modelo SQLAlchemy"""
        try:
            model_name = ''.join(word.capitalize() for word in table_info.name.split('_'))
            
            code = [
                "from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime",
                "from sqlalchemy.orm import relationship",
                "from core.database.base import Base\n\n"
            ]

            code.append(f"class {model_name}(Base):")
            code.append(f'    """Model for table {table_info.name}"""')
            code.append(f"    __tablename__ = '{table_info.name}'")
            if table_info.schema != 'public':
                code.append(f"    __table_args__ = {{'schema': '{table_info.schema}'}}\n")
            else:
                code.append("")

            # Generar columnas
            for col in table_info.columns:
                code.append(self._generate_column_code(col))

            # Generar relationships
            for rel in table_info.relationships:
                target_model = ''.join(word.capitalize() for word in rel['target_table'].split('_'))
                code.append(f"    {rel['target_table']} = relationship('{target_model}')")

            logger.info(f"Generated SQLAlchemy model for '{table_info.name}'")
            return '\n'.join(code)
        except Exception as e:
            logger.error(f"Error generating SQLAlchemy model: {str(e)}")
            raise

    def generate_pydantic_schema(self, table_info: TableInfo) -> str:
        """Genera código del schema Pydantic"""
        try:
            model_name = ''.join(word.capitalize() for word in table_info.name.split('_'))
            
            code = [
                "from pydantic import BaseModel, Field",
                "from typing import Optional",
                "from datetime import datetime\n\n"
            ]

            # Schema Base
            code.append(f"class {model_name}Base(BaseModel):")
            for col in table_info.columns:
                if col.name not in ['id', 'created_at', 'updated_at']:
                    code.append(self._generate_pydantic_field(col))
            code.append("")

            # Schema Create
            code.append(f"class {model_name}Create({model_name}Base):")
            code.append("    pass\n")

            # Schema Update
            code.append(f"class {model_name}Update({model_name}Base):")
            code.append("    pass\n")

            # Schema DB
            code.append(f"class {model_name}InDB({model_name}Base):")
            code.append("    id: int")
            code.append("    created_at: datetime")
            code.append("    updated_at: Optional[datetime] = None\n")
            code.append("    class Config:")
            code.append("        from_attributes = True")

            logger.info(f"Generated Pydantic schemas for '{table_info.name}'")
            return '\n'.join(code)
        except Exception as e:
            logger.error(f"Error generating Pydantic schema: {str(e)}")
            raise

    def _generate_column_code(self, column: ColumnInfo) -> str:
        """Genera código para una columna SQLAlchemy"""
        args = []
        
        # Type
        if column.foreign_key:
            type_str = f"ForeignKey('{column.foreign_key}')"
        else:
            type_str = self._map_to_sqlalchemy_type(column.type)
        
        # Additional arguments
        if column.primary_key:
            args.append("primary_key=True")
        if not column.nullable:
            args.append("nullable=False")
        if column.unique:
            args.append("unique=True")
        if column.default is not None:
            args.append(f"default={column.default}")
        
        args_str = ", ".join([type_str] + args)
        return f"    {column.name} = Column({args_str})"

    def _generate_pydantic_field(self, column: ColumnInfo) -> str:
        """Genera código para un campo Pydantic"""
        type_str = self._map_to_pydantic_type(column.type)
        if column.nullable:
            type_str = f"Optional[{type_str}]"
        
        field_args = []
        if column.default is not None:
            field_args.append(f"default={column.default}")
        
        field_str = f"Field({', '.join(field_args)})" if field_args else ""
        return f"    {column.name}: {type_str}" + (f" = {field_str}" if field_str else "")

    def _map_to_sqlalchemy_type(self, db_type: str) -> str:
        """Mapea tipos de base de datos a tipos SQLAlchemy"""
        type_mapping = {
            'integer': 'Integer',
            'text': 'String',
            'character varying': 'String',
            'boolean': 'Boolean',
            'timestamp': 'DateTime',
            # Agregar más mapeos según sea necesario
        }
        return type_mapping.get(db_type.lower(), 'String')

    def _map_to_pydantic_type(self, db_type: str) -> str:
        """Mapea tipos de base de datos a tipos Python/Pydantic"""
        type_mapping = {
            'integer': 'int',
            'text': 'str',
            'character varying': 'str',
            'boolean': 'bool',
            'timestamp': 'datetime',
            # Agregar más mapeos según sea necesario
        }
        return type_mapping.get(db_type.lower(), 'str')