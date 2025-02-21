# backend\core\generator\model_gen.py
from typing import Dict, List, Optional
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Float, Text
from sqlalchemy.orm import relationship
from core.database.base import Base
from core.metadata.models import TableMetadata, FieldMetadata, RelationshipMetadata

class ModelGenerator:
    """Generador de modelos SQLAlchemy desde metadatos"""
    
    TYPE_MAPPING = {
        'string': String,
        'integer': Integer,
        'boolean': Boolean,
        'datetime': DateTime,
        'float': Float,
        'text': Text,
    }
    
    def __init__(self):
        self.models: Dict[str, type] = {}
    
    def generate_model(self, table_metadata: TableMetadata) -> type:
        """Genera una clase modelo SQLAlchemy desde los metadatos de tabla"""
        attrs = {
            '__tablename__': table_metadata.name,
            '__table_args__': {'schema': table_metadata.schema} if table_metadata.schema != 'public' else None,
        }
        
        # Agregar campos desde los metadatos
        for field in table_metadata.fields:
            attrs[field.name] = self._create_column(field)
        
        # Crear la clase modelo
        model_name = self._generate_class_name(table_metadata.name)
        model = type(model_name, (Base,), attrs)
        
        self.models[table_metadata.name] = model
        return model
    
    def generate_relationships(self, relationships: List[RelationshipMetadata]):
        """Genera las relaciones entre modelos"""
        for rel in relationships:
            source_model = self.models.get(rel.source_table_id)
            target_model = self.models.get(rel.target_table_id)
            
            if source_model and target_model:
                if rel.relationship_type == 'OneToMany':
                    self._add_one_to_many_relationship(source_model, target_model, rel)
                elif rel.relationship_type == 'ManyToOne':
                    self._add_many_to_one_relationship(source_model, target_model, rel)
                elif rel.relationship_type == 'OneToOne':
                    self._add_one_to_one_relationship(source_model, target_model, rel)
    
    def _create_column(self, field_metadata: FieldMetadata) -> Column:
        try:
            # Mapear el tipo
            column_type = self.TYPE_MAPPING.get(field_metadata.field_type.lower())
            if not column_type:
                raise ValueError(f"Tipo de campo no soportado: {field_metadata.field_type}")

            # Preparar argumentos de la columna
            kwargs = {
                'nullable': field_metadata.is_nullable,
                'unique': field_metadata.is_unique,
            }

            # Manejar valor por defecto
            if field_metadata.default_value:
                # Limpiar el valor por defecto de sintaxis PostgreSQL
                default_value = field_metadata.default_value.replace("::character varying", "")
                # Remover comillas simples extra
                default_value = default_value.strip("'")
                
                # Si es un string, mantener las comillas
                if field_metadata.field_type.lower() in ['string', 'text']:
                    kwargs['default'] = default_value
                else:
                    kwargs['default'] = default_value

            # Manejar longitud para strings
            if field_metadata.length and field_metadata.field_type.lower() == 'string':
                return Column(field_metadata.name, String(field_metadata.length), **kwargs)
            
            return Column(field_metadata.name, column_type, **kwargs)

        except Exception as e:
            logger.error(f"Error creando columna {field_metadata.name}: {str(e)}")
            raise
    
    def _generate_class_name(self, table_name: str) -> str:
        """Genera un nombre de clase desde el nombre de la tabla"""
        return ''.join(word.capitalize() for word in table_name.split('_'))
    
    def _add_one_to_many_relationship(self, source_model: type, target_model: type, rel: RelationshipMetadata):
        """Agrega una relación uno a muchos entre modelos"""
        setattr(target_model, f"{rel.source_field}_id", 
                Column(Integer, ForeignKey(f"{source_model.__tablename__}.id")))
        setattr(source_model, f"{rel.target_field}s", 
                relationship(target_model.__name__, back_populates=rel.source_field))
        setattr(target_model, rel.source_field,
                relationship(source_model.__name__, back_populates=f"{rel.target_field}s"))
    
    def _add_many_to_one_relationship(self, source_model: type, target_model: type, rel: RelationshipMetadata):
        """Agrega una relación muchos a uno entre modelos"""
        self._add_one_to_many_relationship(target_model, source_model, rel)
    
    def _add_one_to_one_relationship(self, source_model: type, target_model: type, rel: RelationshipMetadata):
        """Agrega una relación uno a uno entre modelos"""
        setattr(target_model, f"{rel.source_field}_id",
                Column(Integer, ForeignKey(f"{source_model.__tablename__}.id"), unique=True))
        setattr(source_model, rel.target_field,
                relationship(target_model.__name__, uselist=False, back_populates=rel.source_field))
        setattr(target_model, rel.source_field,
                relationship(source_model.__name__, back_populates=rel.target_field))