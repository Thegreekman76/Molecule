# scripts/initialproject/seed_metadata_initial_project.py

import sys
import os
from pathlib import Path
from typing import Dict, List
import logging
from datetime import datetime

# Agregar el directorio raíz del proyecto al PYTHONPATH
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(ROOT_DIR))

from sqlalchemy.exc import IntegrityError
from core.database.database import SessionLocal
from core.metadata.models import TableMetadata, FieldMetadata, RelationshipMetadata

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class BugTrackerMetadataSeeder:
    """Clase para manejar la carga inicial de metadatos del BugTracker"""
    
    def __init__(self):
        self.db = SessionLocal()
        self.tables: Dict[str, TableMetadata] = {}
        self.field_templates: Dict[str, Dict] = {
            'id': {
                'name': 'id',
                'display_name': 'ID',
                'field_type': 'integer',
                'is_nullable': False,
                'is_unique': True,
                'ui_settings': {
                    'visible': False,
                    'readonly': True
                }
            },
            'created_at': {
                'name': 'created_at',
                'display_name': 'Fecha de Creación',
                'field_type': 'datetime',
                'is_nullable': False,
                'default_value': 'CURRENT_TIMESTAMP',
                'ui_settings': {
                    'visible': True,
                    'readonly': True,
                    'widget': 'datetime'
                }
            },
            'updated_at': {
                'name': 'updated_at',
                'display_name': 'Última Actualización',
                'field_type': 'datetime',
                'is_nullable': False,
                'default_value': 'CURRENT_TIMESTAMP',
                'ui_settings': {
                    'visible': True,
                    'readonly': True,
                    'widget': 'datetime'
                }
            },
            'description': {
                'name': 'description',
                'display_name': 'Descripción',
                'field_type': 'text',
                'is_nullable': True,
                'ui_settings': {
                    'widget': 'textarea',
                    'rows': 4
                }
            }
        }

    def create_table_metadata(self, table_data: Dict) -> TableMetadata:
        """Crear metadata de tabla"""
        try:
            table = TableMetadata(
                name=table_data['name'],
                display_name=table_data['display_name'],
                description=table_data.get('description', ''),
                db_schema=table_data.get('db_schema', 'public'),
                is_visible=table_data.get('is_visible', True),
                ui_settings=table_data.get('ui_settings', {})
            )
            self.db.add(table)
            self.db.commit()
            self.db.refresh(table)
            self.tables[table.name] = table
            logger.info(f"✅ Tabla '{table.name}' creada exitosamente")
            return table
        except Exception as e:
            self.db.rollback()
            logger.error(f"❌ Error creando tabla '{table_data['name']}': {str(e)}")
            raise

    def create_field_metadata(self, table: TableMetadata, field_data: Dict) -> FieldMetadata:
        """Crear metadata de campo"""
        try:
            # Si el campo es un template, obtener la configuración base
            base_config = self.field_templates.get(field_data['name'], {})
            field_config = {**base_config, **field_data}  # Merge con prioridad a field_data

            field = FieldMetadata(
                table_id=table.id,
                name=field_config['name'],
                display_name=field_config['display_name'],
                field_type=field_config['field_type'],
                length=field_config.get('length'),
                is_nullable=field_config.get('is_nullable', True),
                is_unique=field_config.get('is_unique', False),
                default_value=field_config.get('default_value'),
                ui_settings=field_config.get('ui_settings', {}),
                validation_rules=field_config.get('validation_rules', {})
            )
            self.db.add(field)
            self.db.commit()
            self.db.refresh(field)
            logger.info(f"✅ Campo '{field.name}' creado en tabla '{table.name}'")
            return field
        except Exception as e:
            self.db.rollback()
            logger.error(f"❌ Error creando campo '{field_data['name']}': {str(e)}")
            raise

    def create_relationship_metadata(self, relationship_data: Dict) -> RelationshipMetadata:
        """Crear metadata de relación"""
        try:
            source_table = self.tables[relationship_data['source_table']]
            target_table = self.tables[relationship_data['target_table']]

            relationship = RelationshipMetadata(
                source_table_id=source_table.id,
                target_table_id=target_table.id,
                relationship_type=relationship_data['type'],
                source_field=relationship_data['source_field'],
                target_field=relationship_data['target_field']
            )
            self.db.add(relationship)
            self.db.commit()
            self.db.refresh(relationship)
            logger.info(f"✅ Relación creada: {source_table.name} -> {target_table.name}")
            return relationship
        except Exception as e:
            self.db.rollback()
            logger.error(f"❌ Error creando relación: {str(e)}")
            raise

    def cleanup_existing_metadata(self):
        """Limpiar metadata existente"""
        try:
            self.db.query(RelationshipMetadata).delete()
            self.db.query(FieldMetadata).delete()
            self.db.query(TableMetadata).delete()
            self.db.commit()
            logger.info("✅ Metadata existente eliminada")
        except Exception as e:
            self.db.rollback()
            logger.error(f"❌ Error limpiando metadata: {str(e)}")
            raise

    def close(self):
        """Cerrar conexión a la base de datos"""
        self.db.close()

    def define_projects_metadata(self):
        """Definir metadata para la tabla de Proyectos"""
        table = self.create_table_metadata({
            'name': 'projects',
            'display_name': 'Proyectos',
            'description': 'Proyectos de desarrollo de software',
            'ui_settings': {
                'icon': 'folder',
                'color': 'blue',
                'list_display': ['name', 'status', 'created_at'],
                'searchable_fields': ['name', 'description'],
                'ordering': ['-created_at']
            }
        })

        # Campos para Proyectos
        fields = [
            {
                'name': 'name',
                'display_name': 'Nombre',
                'field_type': 'string',
                'length': 100,
                'is_nullable': False,
                'is_unique': True,
                'ui_settings': {
                    'widget': 'text',
                    'placeholder': 'Nombre del proyecto',
                    'help_text': 'Ingrese un nombre único para el proyecto'
                },
                'validation_rules': {
                    'min_length': 3,
                    'max_length': 100
                }
            },
            {
                'name': 'description',
                'display_name': 'Descripción',
                'field_type': 'text',
                'is_nullable': True,
                'ui_settings': {
                    'widget': 'rich-text',
                    'rows': 4,
                    'placeholder': 'Descripción detallada del proyecto'
                }
            },
            {
                'name': 'status',
                'display_name': 'Estado',
                'field_type': 'string',
                'length': 20,
                'is_nullable': False,
                'default_value': "'active'",
                'ui_settings': {
                    'widget': 'select',
                    'choices': [
                        {'value': 'active', 'label': 'Activo'},
                        {'value': 'on_hold', 'label': 'En Espera'},
                        {'value': 'completed', 'label': 'Completado'},
                        {'value': 'cancelled', 'label': 'Cancelado'}
                    ]
                }
            },
            {
                'name': 'start_date',
                'display_name': 'Fecha de Inicio',
                'field_type': 'datetime',
                'is_nullable': True,
                'ui_settings': {
                    'widget': 'date'
                }
            },
            {
                'name': 'end_date',
                'display_name': 'Fecha de Finalización',
                'field_type': 'datetime',
                'is_nullable': True,
                'ui_settings': {
                    'widget': 'date'
                }
            }
        ]

        for field_data in fields:
            self.create_field_metadata(table, field_data)

    def define_issues_metadata(self):
        """Definir metadata para la tabla de Issues"""
        table = self.create_table_metadata({
            'name': 'issues',
            'display_name': 'Issues',
            'description': 'Issues y bugs reportados',
            'ui_settings': {
                'icon': 'bug',
                'color': 'red',
                'list_display': ['title', 'status', 'priority', 'assigned_to', 'created_at'],
                'searchable_fields': ['title', 'description'],
                'ordering': ['-priority', '-created_at']
            }
        })

        # Campos para Issues
        fields = [
            {
                'name': 'title',
                'display_name': 'Título',
                'field_type': 'string',
                'length': 200,
                'is_nullable': False,
                'ui_settings': {
                    'widget': 'text',
                    'placeholder': 'Título del issue'
                },
                'validation_rules': {
                    'min_length': 5,
                    'max_length': 200
                }
            },
            {
                'name': 'description',
                'display_name': 'Descripción',
                'field_type': 'text',
                'is_nullable': False,
                'ui_settings': {
                    'widget': 'rich-text',
                    'rows': 6,
                    'placeholder': 'Descripción detallada del issue'
                }
            },
            {
                'name': 'status',
                'display_name': 'Estado',
                'field_type': 'string',
                'length': 20,
                'is_nullable': False,
                'default_value': "'open'",
                'ui_settings': {
                    'widget': 'select',
                    'choices': [
                        {'value': 'open', 'label': 'Abierto'},
                        {'value': 'in_progress', 'label': 'En Progreso'},
                        {'value': 'review', 'label': 'En Revisión'},
                        {'value': 'resolved', 'label': 'Resuelto'},
                        {'value': 'closed', 'label': 'Cerrado'}
                    ]
                }
            },
            {
                'name': 'priority',
                'display_name': 'Prioridad',
                'field_type': 'string',
                'length': 20,
                'is_nullable': False,
                'default_value': "'medium'",
                'ui_settings': {
                    'widget': 'select',
                    'choices': [
                        {'value': 'critical', 'label': 'Crítica'},
                        {'value': 'high', 'label': 'Alta'},
                        {'value': 'medium', 'label': 'Media'},
                        {'value': 'low', 'label': 'Baja'}
                    ]
                }
            },
            {
                'name': 'type',
                'display_name': 'Tipo',
                'field_type': 'string',
                'length': 20,
                'is_nullable': False,
                'default_value': "'bug'",
                'ui_settings': {
                    'widget': 'select',
                    'choices': [
                        {'value': 'bug', 'label': 'Bug'},
                        {'value': 'feature', 'label': 'Nueva Funcionalidad'},
                        {'value': 'improvement', 'label': 'Mejora'},
                        {'value': 'task', 'label': 'Tarea'}
                    ]
                }
            },
            {
                'name': 'assigned_to',
                'display_name': 'Asignado a',
                'field_type': 'integer',
                'is_nullable': True,
                'ui_settings': {
                    'widget': 'user-select',
                    'placeholder': 'Seleccionar usuario'
                }
            },
            {
                'name': 'due_date',
                'display_name': 'Fecha Límite',
                'field_type': 'datetime',
                'is_nullable': True,
                'ui_settings': {
                    'widget': 'date'
                }
            },
            {
                'name': 'estimated_hours',
                'display_name': 'Horas Estimadas',
                'field_type': 'float',
                'is_nullable': True,
                'ui_settings': {
                    'widget': 'number',
                    'min': 0,
                    'step': 0.5
                }
            }
        ]

        for field_data in fields:
            self.create_field_metadata(table, field_data)

    def define_comments_metadata(self):
        """Definir metadata para la tabla de Comentarios"""
        table = self.create_table_metadata({
            'name': 'comments',
            'display_name': 'Comentarios',
            'description': 'Comentarios en issues',
            'ui_settings': {
                'icon': 'message-circle',
                'color': 'gray',
                'list_display': ['content', 'author', 'created_at'],
                'ordering': ['-created_at']
            }
        })

        fields = [
            {
                'name': 'content',
                'display_name': 'Contenido',
                'field_type': 'text',
                'is_nullable': False,
                'ui_settings': {
                    'widget': 'rich-text',
                    'rows': 3,
                    'placeholder': 'Escribe un comentario...'
                }
            },
            {
                'name': 'author_id',
                'display_name': 'Autor',
                'field_type': 'integer',
                'is_nullable': False,
                'ui_settings': {
                    'widget': 'user-select',
                    'readonly': True
                }
            },
            {
                'name': 'issue_id',
                'display_name': 'Issue',
                'field_type': 'integer',
                'is_nullable': False,
                'ui_settings': {
                    'visible': False
                }
            }
        ]

        for field_data in fields:
            self.create_field_metadata(table, field_data)

    def define_tags_metadata(self):
        """Definir metadata para la tabla de Etiquetas"""
        table = self.create_table_metadata({
            'name': 'tags',
            'display_name': 'Etiquetas',
            'description': 'Etiquetas para categorizar issues',
            'ui_settings': {
                'icon': 'tag',
                'color': 'purple',
                'list_display': ['name', 'color', 'created_at'],
                'searchable_fields': ['name']
            }
        })

        fields = [
            {
                'name': 'name',
                'display_name': 'Nombre',
                'field_type': 'string',
                'length': 50,
                'is_nullable': False,
                'is_unique': True,
                'ui_settings': {
                    'widget': 'text',
                    'placeholder': 'Nombre de la etiqueta'
                }
            },
            {
                'name': 'color',
                'display_name': 'Color',
                'field_type': 'string',
                'length': 7,
                'is_nullable': False,
                'default_value': "'#6B7280'",
                'ui_settings': {
                    'widget': 'color-picker'
                }
            },
            {
                'name': 'description',
                'display_name': 'Descripción',
                'field_type': 'string',
                'length': 200,
                'is_nullable': True,
                'ui_settings': {
                    'widget': 'text',
                    'placeholder': 'Descripción breve de la etiqueta'
                }
            }
        ]

        for field_data in fields:
            self.create_field_metadata(table, field_data)

    def define_issue_history_metadata(self):
        """Definir metadata para la tabla de Historial de Issues"""
        table = self.create_table_metadata({
            'name': 'issue_history',
            'display_name': 'Historial de Issues',
            'description': 'Registro de cambios en issues',
            'ui_settings': {
                'icon': 'history',
                'color': 'orange',
                'list_display': ['field_changed', 'old_value', 'new_value', 'changed_by', 'created_at'],
                'ordering': ['-created_at']
            }
        })

        fields = [
            {
                'name': 'issue_id',
                'display_name': 'Issue',
                'field_type': 'integer',
                'is_nullable': False,
                'ui_settings': {
                    'visible': False
                }
            },
            {
                'name': 'field_changed',
                'display_name': 'Campo Modificado',
                'field_type': 'string',
                'length': 50,
                'is_nullable': False,
                'ui_settings': {
                    'widget': 'text',
                    'readonly': True
                }
            },
            {
                'name': 'old_value',
                'display_name': 'Valor Anterior',
                'field_type': 'text',
                'is_nullable': True,
                'ui_settings': {
                    'widget': 'text',
                    'readonly': True
                }
            },
            {
                'name': 'new_value',
                'display_name': 'Nuevo Valor',
                'field_type': 'text',
                'is_nullable': True,
                'ui_settings': {
                    'widget': 'text',
                    'readonly': True
                }
            },
            {
                'name': 'changed_by',
                'display_name': 'Modificado Por',
                'field_type': 'integer',
                'is_nullable': False,
                'ui_settings': {
                    'widget': 'user-select',
                    'readonly': True
                }
            }
        ]

        for field_data in fields:
            self.create_field_metadata(table, field_data)

    def define_issue_tags_metadata(self):
        """Definir metadata para la tabla de relación Issues-Tags"""
        table = self.create_table_metadata({
            'name': 'issue_tags',
            'display_name': 'Etiquetas de Issues',
            'description': 'Relación entre issues y etiquetas',
            'is_visible': False,
            'ui_settings': {
                'hidden': True
            }
        })

        fields = [
            {
                'name': 'issue_id',
                'display_name': 'Issue',
                'field_type': 'integer',
                'is_nullable': False
            },
            {
                'name': 'tag_id',
                'display_name': 'Etiqueta',
                'field_type': 'integer',
                'is_nullable': False
            }
        ]

        for field_data in fields:
            self.create_field_metadata(table, field_data)

    def define_relationships(self):
        """Definir las relaciones entre tablas"""
        relationships = [
            # Issues pertenecen a un Proyecto
            {
                'source_table': 'issues',
                'target_table': 'projects',
                'type': 'ManyToOne',
                'source_field': 'project_id',
                'target_field': 'id'
            },
            # Comentarios pertenecen a un Issue
            {
                'source_table': 'comments',
                'target_table': 'issues',
                'type': 'ManyToOne',
                'source_field': 'issue_id',
                'target_field': 'id'
            },
            # Issues tienen muchas Etiquetas
            {
                'source_table': 'issue_tags',
                'target_table': 'issues',
                'type': 'ManyToOne',
                'source_field': 'issue_id',
                'target_field': 'id'
            },
            {
                'source_table': 'issue_tags',
                'target_table': 'tags',
                'type': 'ManyToOne',
                'source_field': 'tag_id',
                'target_field': 'id'
            },
            # Historial pertenece a un Issue
            {
                'source_table': 'issue_history',
                'target_table': 'issues',
                'type': 'ManyToOne',
                'source_field': 'issue_id',
                'target_field': 'id'
            }
        ]

        for relationship_data in relationships:
            self.create_relationship_metadata(relationship_data)


def seed_initial_project():
    """Función principal para ejecutar la carga inicial de datos"""
    logger.info("🚀 Iniciando carga de metadatos del proyecto BugTracker")
    
    try:
        seeder = BugTrackerMetadataSeeder()
        
        # Limpiar metadata existente
        logger.info("\n🧹 Limpiando metadata existente...")
        seeder.cleanup_existing_metadata()
        
        # Crear tablas principales
        logger.info("\n📊 Creando tablas principales...")
        seeder.define_projects_metadata()
        seeder.define_issues_metadata()
        
        # Crear tablas auxiliares
        logger.info("\n📋 Creando tablas auxiliares...")
        seeder.define_comments_metadata()
        seeder.define_tags_metadata()
        seeder.define_issue_history_metadata()
        seeder.define_issue_tags_metadata()
        
        # Crear relaciones
        logger.info("\n🔗 Creando relaciones entre tablas...")
        seeder.define_relationships()
        
        logger.info("\n✨ Carga de metadatos completada exitosamente!")
        
    except Exception as e:
        logger.error(f"\n❌ Error durante la carga de metadatos: {str(e)}")
        raise
    finally:
        seeder.close()

if __name__ == "__main__":
    try:
        seed_initial_project()
    except Exception as e:
        logger.error(f"Error fatal: {str(e)}")
        sys.exit(1)