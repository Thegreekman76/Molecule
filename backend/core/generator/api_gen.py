# backend/core/generator/api_gen.py
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
        router = APIRouter()
        
        # Crear schemas Pydantic
        create_schema = self._generate_create_schema(table_metadata, model)
        update_schema = self._generate_update_schema(table_metadata, model)
        response_schema = self._generate_response_schema(table_metadata, model)
        
        # Endpoints CRUD
        @router.post("/", response_model=response_schema)
        async def create_item(item: create_schema, db: Session = Depends(get_db)):
            db_item = model(**item.dict())
            db.add(db_item)
            try:
                db.commit()
                db.refresh(db_item)
                return db_item
            except Exception as e:
                db.rollback()
                raise HTTPException(status_code=400, detail=str(e))
        
        @router.get("/", response_model=List[response_schema])
        async def read_items(
            skip: int = 0, 
            limit: int = 100, 
            db: Session = Depends(get_db)
        ):
            items = db.query(model).offset(skip).limit(limit).all()
            return items
        
        @router.get("/{item_id}", response_model=response_schema)
        async def read_item(item_id: int, db: Session = Depends(get_db)):
            item = db.query(model).filter(model.id == item_id).first()
            if item is None:
                raise HTTPException(status_code=404, detail="Item not found")
            return item
        
        @router.put("/{item_id}", response_model=response_schema)
        async def update_item(
            item_id: int, 
            item: update_schema, 
            db: Session = Depends(get_db)
        ):
            db_item = db.query(model).filter(model.id == item_id).first()
            if db_item is None:
                raise HTTPException(status_code=404, detail="Item not found")
            
            for key, value in item.dict(exclude_unset=True).items():
                setattr(db_item, key, value)
            
            try:
                db.commit()
                db.refresh(db_item)
                return db_item
            except Exception as e:
                db.rollback()
                raise HTTPException(status_code=400, detail=str(e))
        
        @router.delete("/{item_id}")
        async def delete_item(item_id: int, db: Session = Depends(get_db)):
            db_item = db.query(model).filter(model.id == item_id).first()
            if db_item is None:
                raise HTTPException(status_code=404, detail="Item not found")
            
            try:
                db.delete(db_item)
                db.commit()
                return {"ok": True}
            except Exception as e:
                db.rollback()
                raise HTTPException(status_code=400, detail=str(e))
        
        # Agregar endpoints personalizados según la metadata
        self._add_custom_endpoints(router, table_metadata, model)
        
        self.routers[table_metadata.name] = router
        return router
    
    def _generate_create_schema(
        self, 
        table_metadata: TableMetadata, 
        model: Type
    ) -> Type:
        """Genera el schema Pydantic para creación"""
        fields = {}
        for field in table_metadata.fields:
            if field.name not in ['id', 'created_at', 'updated_at']:
                field_type = self._get_pydantic_type(field)
                fields[field.name] = (field_type, ... if not field.is_nullable else None)
        
        return create_model(
            f'{model.__name__}Create',
            **fields
        )
    
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
            fields[field.name] = (field_type, ... if not field.is_nullable else None)
        
        return create_model(
            f'{model.__name__}Response',
            **fields
        )
    
    def _get_pydantic_type(self, field: FieldMetadata) -> Type:
        """Obtiene el tipo Pydantic correspondiente al tipo de campo"""
        type_mapping = {
            'string': str,
            'integer': int,
            'boolean': bool,
            'datetime': str,  # ISO format string
            'float': float,
            'text': str,
        }
        return type_mapping.get(field.field_type, str)
    
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