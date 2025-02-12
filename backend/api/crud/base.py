# api/crud/base.py
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core.database.database import get_db
from models.base import Base
from schemas.base import BaseSchema, BaseCreateSchema, BaseUpdateSchema, BaseInDBSchema
from utils.helpers import CRUDHelper

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseCreateSchema)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseUpdateSchema)
InDBSchemaType = TypeVar("InDBSchemaType", bound=BaseInDBSchema)

class BaseCRUDRouter(Generic[ModelType, CreateSchemaType, UpdateSchemaType, InDBSchemaType]):
    """Base class for CRUD routers"""
    
    def __init__(
        self,
        model: Type[ModelType],
        create_schema: Type[CreateSchemaType],
        update_schema: Type[UpdateSchemaType],
        indb_schema: Type[InDBSchemaType],
        prefix: str,
    ):
        self.model = model
        self.create_schema = create_schema
        self.update_schema = update_schema
        self.indb_schema = indb_schema
        self.router = APIRouter(prefix=prefix)
        self.crud = CRUDHelper[ModelType, CreateSchemaType, UpdateSchemaType](model)
        
        # Register routes
        self._register_routes()
    
    def _register_routes(self):
        """Register all CRUD routes"""
        
        @self.router.post("/", response_model=self.indb_schema)
        async def create(
            obj_in: self.create_schema,
            db: Session = Depends(get_db)
        ):
            """Create new record"""
            return await self.crud.create(db, obj_in=obj_in)

        @self.router.get("/{id}", response_model=self.indb_schema)
        async def read(id: int, db: Session = Depends(get_db)):
            """Get record by ID"""
            db_obj = await self.crud.get(db, id)
            if db_obj is None:
                raise HTTPException(status_code=404, detail="Object not found")
            return db_obj

        @self.router.get("/", response_model=List[self.indb_schema])
        async def read_multi(
            skip: int = 0,
            limit: int = 100,
            db: Session = Depends(get_db)
        ):
            """Get multiple records"""
            return await self.crud.get_multi(db, skip=skip, limit=limit)

        @self.router.put("/{id}", response_model=self.indb_schema)
        async def update(
            id: int,
            obj_in: self.update_schema,
            db: Session = Depends(get_db)
        ):
            """Update record"""
            db_obj = await self.crud.get(db, id)
            if db_obj is None:
                raise HTTPException(status_code=404, detail="Object not found")
            return await self.crud.update(db, db_obj=db_obj, obj_in=obj_in)

        @self.router.delete("/{id}", response_model=self.indb_schema)
        async def delete(id: int, db: Session = Depends(get_db)):
            """Delete record"""
            return await self.crud.delete(db, id=id)

