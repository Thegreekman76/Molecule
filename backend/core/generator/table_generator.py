# core/generator/table_generator.py
from sqlalchemy import Table, Column, Integer, String, Float, ForeignKey, DateTime, Text, Boolean, MetaData, Numeric, text, inspect
from core.database.database import engine
from core.metadata.models import TableMetadata, FieldMetadata, RelationshipMetadata
from sqlalchemy.schema import CreateTable
import logging

logger = logging.getLogger(__name__)

class TableGenerator:
    def __init__(self, engine):
        self.engine = engine
        self.metadata = MetaData()
        self.inspector = inspect(engine)
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

            # Obtener lista de tablas existentes
            existing_tables = self.inspector.get_table_names()
            logger.info(f"Tablas existentes en la base de datos: {existing_tables}")
            
            created_tables = []

            for table_meta in tables_metadata:
                try:
                    logger.info(f"\nProcesando tabla: {table_meta.name}")
                    
                    # Verificar si la tabla ya existe
                    if table_meta.name in existing_tables:
                        logger.info(f"La tabla {table_meta.name} ya existe, saltando...")
                        continue

                    # Obtener campos de la tabla
                    fields = db.query(FieldMetadata).filter(
                        FieldMetadata.table_id == table_meta.id
                    ).all()

                    logger.info(f"Campos encontrados para {table_meta.name}:")
                    for field in fields:
                        logger.info(f"  - {field.name} ({field.field_type})")

                    # Crear columnas
                    columns = []
                    # Asegurar que existe la columna ID
                    columns.append(Column('id', Integer, primary_key=True))
                    logger.info("Agregada columna 'id' automáticamente")
                    
                    for field in fields:
                        if field.name != 'id':  # Saltamos el id porque ya lo agregamos
                            try:
                                column = self._create_column(field)
                                if column:
                                    columns.append(column)
                                    logger.info(f"Columna {field.name} creada exitosamente")
                                else:
                                    logger.warning(f"No se pudo crear la columna {field.name}")
                            except Exception as col_error:
                                logger.error(f"Error creando columna {field.name}: {str(col_error)}")

                    # Agregar timestamps
                    columns.extend([
                        Column('created_at', DateTime, server_default=text('CURRENT_TIMESTAMP')),
                        Column('updated_at', DateTime, onupdate=text('CURRENT_TIMESTAMP'))
                    ])
                    logger.info("Agregadas columnas de timestamp")

                    # Crear tabla
                    logger.info(f"Creando tabla {table_meta.name} con {len(columns)} columnas")
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
                    created_tables.append(table_meta.name)
                    logger.info(f"✅ Tabla {table_meta.name} creada exitosamente")

                except Exception as e:
                    logger.error(f"❌ Error creando tabla {table_meta.name}: {str(e)}", exc_info=True)
                    continue

            # Crear relaciones después de que todas las tablas existan
            self._create_relationships(db)
            
            return created_tables

        except Exception as e:
            logger.error(f"Error en la generación de tablas: {str(e)}", exc_info=True)
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
                column_args['server_default'] = text(field.default_value)

            # Crear la columna
            return Column(
                field.name,
                column_type,
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