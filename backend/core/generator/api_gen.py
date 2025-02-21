# backend\core\generator\api_gen.py
from datetime import datetime
from typing import Type, Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import create_model
from core.database.database import get_db
from core.metadata.models import TableMetadata, FieldMetadata

class APIGenerator:
    """Generador de endpoints FastAPI desde metadatos"""
    
    def __init__(self):
        self.routers: Dict[str, APIRouter] = {}
    
    def generate_router(self, table_metadata: TableMetadata, model: Type) -> APIRouter:
        """Genera un router FastAPI para un modelo específico"""
        try:
            router = APIRouter()
            
            # Crear schemas Pydantic
            create_schema = self._generate_create_schema(table_metadata, model)
            update_schema = self._generate_update_schema(table_metadata, model)
            
            # Función auxiliar para serializar respuestas
            def serialize_model(db_obj):
                """Serializa los objetos del modelo, convirtiendo datetime a ISO format"""
                result = {}
                for column in model.__table__.columns:
                    value = getattr(db_obj, column.name)
                    if isinstance(value, datetime):
                        result[column.name] = value.isoformat()
                    else:
                        result[column.name] = value
                return result
            
            # Endpoints CRUD
            @router.post("/")
            async def create_item(item: create_schema, db: Session = Depends(get_db)):
                """Crear nuevo item"""
                try:
                    # Convertir Pydantic model a dict
                    item_data = item.dict()
                    
                    # Crear y guardar el objeto
                    db_item = model(**item_data)
                    db.add(db_item)
                    db.commit()
                    db.refresh(db_item)
                    
                    # Serializar la respuesta
                    return serialize_model(db_item)
                except Exception as e:
                    db.rollback()
                    raise HTTPException(status_code=400, detail=str(e))
            
            @router.get("/")
            async def read_items(
                skip: int = 0, 
                limit: int = 100, 
                db: Session = Depends(get_db)
            ):
                """Obtener lista de items"""
                items = db.query(model).offset(skip).limit(limit).all()
                # Serializar cada item en la lista
                return [serialize_model(item) for item in items]
            
            @router.get("/{item_id}")
            async def read_item(item_id: int, db: Session = Depends(get_db)):
                """Obtener un item específico"""
                item = db.query(model).filter(model.id == item_id).first()
                if item is None:
                    raise HTTPException(status_code=404, detail="Item not found")
                # Serializar la respuesta
                return serialize_model(item)
            
            @router.put("/{item_id}")
            async def update_item(
                item_id: int, 
                item: update_schema, 
                db: Session = Depends(get_db)
            ):
                """Actualizar un item"""
                db_item = db.query(model).filter(model.id == item_id).first()
                if db_item is None:
                    raise HTTPException(status_code=404, detail="Item not found")
                
                # Actualizar solo los campos proporcionados
                for key, value in item.dict(exclude_unset=True).items():
                    if hasattr(db_item, key):
                        setattr(db_item, key, value)
                
                try:
                    db.commit()
                    db.refresh(db_item)
                    # Serializar la respuesta
                    return serialize_model(db_item)
                except Exception as e:
                    db.rollback()
                    raise HTTPException(status_code=400, detail=str(e))
            
            @router.delete("/{item_id}")
            async def delete_item(item_id: int, db: Session = Depends(get_db)):
                """Eliminar un item"""
                db_item = db.query(model).filter(model.id == item_id).first()
                if db_item is None:
                    raise HTTPException(status_code=404, detail="Item not found")
                
                try:
                    # Serializar antes de eliminar
                    response = serialize_model(db_item)
                    db.delete(db_item)
                    db.commit()
                    return response
                except Exception as e:
                    db.rollback()
                    raise HTTPException(status_code=400, detail=str(e))
            
            return router

        except Exception as e:
            logger.error(f"Error generating router: {str(e)}")
            raise
    
    def _generate_create_schema(
        self, 
        table_metadata: TableMetadata, 
        model: Type
    ) -> Type:
        """Genera el schema Pydantic para creación"""
        try:
            fields = {}
            if not hasattr(table_metadata, 'fields'):
                print(f"Warning: table_metadata no tiene campos para {table_metadata.name}")
                return create_model(f'{model.__name__}Create', __annotations__={})
                
            for field in table_metadata.fields:
                print(f"Procesando campo: {field.name} - tipo: {field.field_type}")
                if field.name not in ['id', 'created_at', 'updated_at']:
                    field_type = self._get_pydantic_type(field)
                    fields[field.name] = (field_type, ... if not field.is_nullable else None)
            
            return create_model(
                f'{model.__name__}Create',
                **fields
            )
        except Exception as e:
            print(f"Error en generate_create_schema: {str(e)}")
            raise
        
    
    def _generate_update_schema(
        self, 
        table_metadata: TableMetadata, 
        model: Type
    ) -> Type:
        """Genera el schema Pydantic para actualización"""
        fields = {}
        for field in table_metadata.fields:
            if field.name not in ['id', 'created_at', 'updated_at']:
                field_type = self._get_pydantic_type(field)
                fields[field.name] = (Optional[field_type], None)
        
        return create_model(
            f'{model.__name__}Update',
            **fields
        )
    
    def _generate_response_schema(
        self, 
        table_metadata: TableMetadata, 
        model: Type
    ) -> Type:
        """Genera el schema Pydantic para respuesta"""
        fields = {}
        for field in table_metadata.fields:
            field_type = self._get_pydantic_type(field)
            if field_type == datetime:
                fields[field.name] = (field_type, ... if not field.is_nullable else None)
            else:
                fields[field.name] = (field_type, ... if not field.is_nullable else None)
        
        # Configurar serialización de datetime
        model_config = {
            "json_encoders": {
                datetime: lambda v: v.isoformat() if v else None
            }
        }
        
        return create_model(
            f'{model.__name__}Response',
            __config__=type('Config', (), {"json_encoders": {datetime: lambda v: v.isoformat() if v else None}}),
            **fields
        )
    
    def _get_pydantic_type(self, field: FieldMetadata) -> Type:
        """Obtiene el tipo Pydantic correspondiente al tipo de campo"""
        try:
            field_type = field.field_type.lower() if field.field_type else 'string'
            type_mapping = {
                'string': str,
                'integer': int,
                'boolean': bool,
                'datetime': str,  # ISO format string
                'float': float,
                'text': str,
            }
            return type_mapping.get(field_type, str)
        except Exception as e:
            print(f"Error getting type for field {field.name}: {str(e)}")
            return str  # tipo por defecto
    
    def _add_custom_endpoints(
        self, 
        router: APIRouter, 
        table_metadata: TableMetadata, 
        model: Type
    ):
        """Agrega endpoints personalizados según la metadata"""
        # TODO: Implementar lógica para endpoints personalizados
        # Por ejemplo, endpoints de búsqueda, filtrado, agregación, etc.
        pass