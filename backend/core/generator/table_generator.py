# backend\core\generator\table_generator.py
from sqlalchemy import JSON, Table, Column, Integer, String, Float, ForeignKey, DateTime, Text, Boolean, MetaData, Numeric, text, inspect
from core.database.database import engine
from sqlalchemy.dialects.postgresql import JSONB
from core.metadata.models import TableMetadata, FieldMetadata, RelationshipMetadata
from sqlalchemy.schema import CreateTable
import logging
from collections import defaultdict
from typing import Dict, List, Set

logger = logging.getLogger(__name__)

class TableGenerator:
    def __init__(self, engine):
        self.engine = engine
        self.metadata = MetaData()
        self.inspector = inspect(engine)
        self.type_mapping = {
            'string': String,
            'integer': Integer,
            'boolean': Boolean,
            'datetime': DateTime,
            'float': Float,
            'decimal': Numeric,
            'text': Text,
            'varchar': String,
            'timestamp': DateTime,
            'json': JSON,
            'jsonb': JSONB,
        }

    def _build_dependency_graph(self, db) -> Dict[str, Set[str]]:
        """Construye un grafo de dependencias entre tablas"""
        dependencies = defaultdict(set)
        relationships = db.query(RelationshipMetadata).all()
        
        for rel in relationships:
            source_table = db.query(TableMetadata).get(rel.source_table_id)
            target_table = db.query(TableMetadata).get(rel.target_table_id)
            
            if source_table and target_table:
                # La tabla source depende de target (necesita que target exista primero)
                dependencies[source_table.name].add(target_table.name)
                
        return dependencies

    def _get_creation_order(self, dependencies: Dict[str, Set[str]]) -> List[str]:
        """Obtiene el orden de creación de tablas basado en dependencias"""
        visited = set()
        temp_mark = set()
        order = []

        def visit(node: str):
            if node in temp_mark:
                raise ValueError(f"Dependencia circular detectada con tabla {node}")
            if node not in visited:
                temp_mark.add(node)
                for dep in dependencies.get(node, set()):
                    visit(dep)
                temp_mark.remove(node)
                visited.add(node)
                order.append(node)

        # Visitar cada nodo
        for node in dependencies.keys():
            if node not in visited:
                visit(node)

        # Agregar tablas sin dependencias
        all_tables = set(dependencies.keys()).union(*dependencies.values())
        standalone_tables = [t for t in all_tables if t not in order]
        return standalone_tables + order

    def generate_tables(self, db):
        """Genera las tablas físicas desde la metadata"""
        try:
            tables_metadata = db.query(TableMetadata).all()
            logger.info(f"Encontradas {len(tables_metadata)} tablas en metadata")

            for table_meta in tables_metadata:
                try:
                    logger.info(f"\n=== Procesando tabla: {table_meta.name} ===")
                    
                    # Obtener campos de la tabla y mostrar la consulta SQL
                    fields_query = db.query(FieldMetadata).filter(FieldMetadata.table_id == table_meta.id)
                    logger.info("Campos encontrados:")
                    fields = fields_query.all()

                    # Crear columnas
                    columns = []
                    # Asegurar que existe la columna ID
                    columns.append(Column('id', Integer, primary_key=True))
                    logger.info("✅ Agregada columna 'id' automáticamente")
                    
                    # Agregar timestamps (importante)
                    columns.append(Column('created_at', DateTime, server_default=text('CURRENT_TIMESTAMP')))
                    columns.append(Column('updated_at', DateTime, server_default=text('CURRENT_TIMESTAMP'), onupdate=text('CURRENT_TIMESTAMP')))
                    logger.info("✅ Agregadas columnas de timestamp")
                    
                    for field in fields:
                        try:
                            # Debug de cada campo
                            logger.info(f"\nProcesando campo: {field.name}")
                            logger.info(f"Tipo: {field.field_type}")
                            logger.info(f"Length: {field.length}")
                            logger.info(f"Nullable: {field.is_nullable}")
                            logger.info(f"Unique: {field.is_unique}")
                            logger.info(f"Default: {field.default_value}")

                            # Obtener tipo de columna
                            field_type = self.type_mapping.get(field.field_type.lower())
                            if not field_type:
                                logger.warning(f"⚠️ Tipo no soportado: {field.field_type}, usando String")
                                field_type = String

                            # Crear argumentos de la columna
                            column_args = {
                                'nullable': field.is_nullable,
                                'unique': field.is_unique
                            }

                            # Manejar length para strings
                            if field.length and field_type == String:
                                field_type = String(field.length)

                            # Manejar valor por defecto
                            if field.default_value:
                                column_args['server_default'] = text(field.default_value)

                            # Crear columna
                            column = Column(field.name, field_type, **column_args)
                            columns.append(column)
                            logger.info(f"✅ Columna {field.name} creada exitosamente")

                        except Exception as e:
                            logger.error(f"❌ Error creando columna {field.name}: {str(e)}")
                            raise

                    # Crear tabla
                    logger.info(f"\nCreando tabla {table_meta.name} con {len(columns)} columnas")
                    table = Table(
                        table_meta.name,
                        self.metadata,
                        *columns,
                        schema=table_meta.db_schema
                    )

                    # Generar SQL
                    create_sql = str(CreateTable(table).compile(self.engine))
                    logger.info(f"SQL generado:\n{create_sql}")

                    # Crear tabla
                    table.create(self.engine)
                    logger.info(f"✅ Tabla {table_meta.name} creada exitosamente")

                except Exception as e:
                    logger.error(f"❌ Error procesando tabla {table_meta.name}: {str(e)}")
                    raise

        except Exception as e:
            logger.error(f"Error en generate_tables: {str(e)}")
            raise

    def _create_column(self, field):
        try:
            logger.info(f"Procesando campo: {field.name} - Tipo: {field.field_type}")
            
            # Mapeo de tipo
            field_type = field.field_type.lower()
            column_type = self.type_mapping.get(field_type)
            if not column_type:
                logger.warning(f"Tipo {field_type} no encontrado, usando String")
                column_type = String

            # Argumentos base de la columna
            column_args = {}
            
            # Si es String o Text y tiene length
            if field.length and (column_type == String):
                column_type = String(field.length)
            
            # Configurar nullable y unique
            if not field.is_nullable:
                column_args['nullable'] = False
            if field.is_unique:
                column_args['unique'] = True
                
            # Valor por defecto
            if field.default_value:
                if "CURRENT_TIMESTAMP" in str(field.default_value).upper():
                    column_args['server_default'] = text('CURRENT_TIMESTAMP')
                else:
                    column_args['server_default'] = text(str(field.default_value))

            # Crear columna
            column = Column(field.name, column_type, **column_args)
            logger.info(f"✅ Columna {field.name} creada con: {column_args}")
            return column

        except Exception as e:
            logger.error(f"❌ Error creando columna {field.name}: {str(e)}")
            raise

    def _create_relationships(self, db):
        """Crea las relaciones entre tablas"""
        try:
            relationships = db.query(RelationshipMetadata).all()
            logger.info(f"Creando {len(relationships)} relaciones")

            # Obtener lista de tablas existentes
            existing_tables = self.inspector.get_table_names()

            for rel in relationships:
                try:
                    source_table = db.query(TableMetadata).get(rel.source_table_id)
                    target_table = db.query(TableMetadata).get(rel.target_table_id)

                    if not source_table or not target_table:
                        continue

                    if source_table.name not in existing_tables:
                        logger.warning(f"Tabla origen {source_table.name} no existe")
                        continue

                    if target_table.name not in existing_tables:
                        logger.warning(f"Tabla destino {target_table.name} no existe")
                        continue

                    # Crear la foreign key
                    fk_name = f"fk_{source_table.name}_{target_table.name}"
                    column_name = f"{rel.source_field}"
                    
                    # Agregar la columna de foreign key
                    with self.engine.begin() as conn:
                        # Primero agregar la columna si no existe
                        conn.execute(text(
                            f"ALTER TABLE {source_table.name} "
                            f"ADD COLUMN IF NOT EXISTS {column_name} INTEGER"
                        ))
                        
                        # Luego agregar la foreign key
                        conn.execute(text(
                            f"ALTER TABLE {source_table.name} "
                            f"ADD CONSTRAINT {fk_name} "
                            f"FOREIGN KEY ({column_name}) "
                            f"REFERENCES {target_table.name} ({rel.target_field})"
                        ))

                    logger.info(f"✅ Relación creada: {source_table.name} -> {target_table.name}")

                except Exception as e:
                    logger.error(f"Error creando relación: {str(e)}")
                    continue

        except Exception as e:
            logger.error(f"Error en la creación de relaciones: {str(e)}")
            raise