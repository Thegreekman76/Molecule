# core/generator/table_generator.py
from sqlalchemy import Table, Column, Integer, String, Float, ForeignKey, DateTime, Text, Boolean, MetaData, Numeric
from core.database.database import engine
from core.metadata.models import TableMetadata, FieldMetadata, RelationshipMetadata
from sqlalchemy.schema import CreateTable
import logging

logger = logging.getLogger(__name__)

class TableGenerator:
    def __init__(self, engine):
        self.engine = engine
        self.metadata = MetaData()
        self.type_mapping = {
            'integer': Integer,
            'string': String,
            'varchar': String,
            'text': Text,
            'float': Float,
            'decimal': Numeric,
            'datetime': DateTime,
            'timestamp': DateTime,
            'boolean': Boolean,
        }

    def generate_tables(self, db):
        """Genera las tablas físicas desde la metadata"""
        try:
            tables_metadata = db.query(TableMetadata).all()
            logger.info(f"Encontradas {len(tables_metadata)} tablas en metadata")

            created_tables = []
            for table_meta in tables_metadata:
                try:
                    # Verificar si la tabla ya existe
                    if engine.dialect.has_table(engine, table_meta.name):
                        logger.info(f"La tabla {table_meta.name} ya existe")
                        continue

                    fields = db.query(FieldMetadata).filter(
                        FieldMetadata.table_id == table_meta.id
                    ).all()

                    logger.info(f"Creando tabla {table_meta.name} con {len(fields)} campos")
                    
                    # Crear columnas
                    columns = []
                    for field in fields:
                        column = self._create_column(field)
                        if column:
                            columns.append(column)

                    # Crear tabla
                    table = Table(
                        table_meta.name,
                        self.metadata,
                        *columns,
                        schema=table_meta.db_schema
                    )
                    
                    # Generar SQL y crear tabla
                    table.create(self.engine)
                    created_tables.append(table_meta.name)
                    logger.info(f"✅ Tabla {table_meta.name} creada exitosamente")

                except Exception as e:
                    logger.error(f"Error creando tabla {table_meta.name}: {str(e)}")
                    continue

            # Crear relaciones después de que todas las tablas existan
            self._create_relationships(db)
            
            return created_tables

        except Exception as e:
            logger.error(f"Error en la generación de tablas: {str(e)}")
            raise

    def _create_column(self, field):
        """Crea una columna SQLAlchemy desde un campo de metadata"""
        try:
            # Obtener el tipo de columna
            column_type = self.type_mapping.get(field.field_type.lower())
            if not column_type:
                logger.warning(f"Tipo de campo no soportado: {field.field_type}")
                column_type = String

            # Configurar argumentos de la columna
            column_args = {
                'nullable': field.is_nullable,
                'unique': field.is_unique
            }

            # Manejar longitud para tipos que la soportan
            if field.length and issubclass(column_type, (String, Text)):
                column_args['length'] = field.length

            # Manejar valores por defecto
            if field.default_value is not None:
                column_args['server_default'] = field.default_value

            # Crear la columna
            return Column(
                field.name,
                column_type,
                *([ForeignKey(field.foreign_key)] if field.foreign_key else []),
                **column_args
            )

        except Exception as e:
            logger.error(f"Error creando columna {field.name}: {str(e)}")
            return None

    def _create_relationships(self, db):
        """Crea las relaciones entre tablas"""
        try:
            relationships = db.query(RelationshipMetadata).all()
            logger.info(f"Creando {len(relationships)} relaciones")

            for rel in relationships:
                try:
                    source_table = db.query(TableMetadata).get(rel.source_table_id)
                    target_table = db.query(TableMetadata).get(rel.target_table_id)

                    if not source_table or not target_table:
                        continue

                    # Crear la foreign key
                    fk_name = f"fk_{source_table.name}_{target_table.name}"
                    column_name = f"{rel.source_field}"
                    
                    if not engine.dialect.has_table(engine, source_table.name):
                        logger.warning(f"Tabla {source_table.name} no existe")
                        continue

                    # Agregar la columna de foreign key
                    with engine.begin() as conn:
                        conn.execute(text(
                            f"ALTER TABLE {source_table.name} "
                            f"ADD COLUMN IF NOT EXISTS {column_name} INTEGER"
                        ))
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