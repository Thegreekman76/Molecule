# backend\utils\helpers.py
from typing import Any, Dict, List, Optional, Type, TypeVar, Generic
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from models.base import Base
from schemas.base import BaseSchema, BaseCreateSchema, BaseUpdateSchema

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseCreateSchema)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseUpdateSchema)

class CRUDHelper(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """Base class for CRUD operations"""
    
    def __init__(self, model: Type[ModelType]):
        self.model = model

    def get(self, db: Session, id: int) -> Optional[ModelType]:
        """Get a record by ID"""
        return db.query(self.model).filter(self.model.id == id).first()

    def get_multi(
        self, 
        db: Session, 
        *, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[ModelType]:
        """Get multiple records"""
        return db.query(self.model).offset(skip).limit(limit).all()

    def create(
        self, 
        db: Session, 
        *, 
        obj_in: CreateSchemaType
    ) -> ModelType:
        """Create a new record"""
        obj_in_data = obj_in.model_dump() if hasattr(obj_in, 'model_dump') else obj_in.dict()
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self,
        db: Session,
        *,
        db_obj: ModelType,
        obj_in: UpdateSchemaType | Dict[str, Any]
    ) -> ModelType:
        """Update a record"""
        obj_data = db_obj.dict()
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump() if hasattr(obj_in, 'model_dump') else obj_in.dict(exclude_unset=True)
            
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
                
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, *, id: int) -> ModelType:
        """Delete a record"""
        obj = self.get(db, id)
        if not obj:
            raise HTTPException(status_code=404, detail="Object not found")
        db.delete(obj)
        db.commit()
        return obj

    def exists(self, db: Session, id: int) -> bool:
        """Check if a record exists"""
        result = db.query(self.model).filter(self.model.id == id).first()
        return result is not None