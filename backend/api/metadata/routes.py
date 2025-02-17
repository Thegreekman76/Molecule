# backend\api\metadata\routes.py
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List
from core.database.database import get_db
from core.metadata.models import TableMetadata, FieldMetadata, RelationshipMetadata
from core.metadata.schema import (
    TableMetadataCreate,
    TableMetadataUpdate,
    TableMetadataInDB,
    FieldMetadataCreate,
    FieldMetadataUpdate,
    FieldMetadataInDB,
    RelationshipMetadataCreate,
    RelationshipMetadataUpdate,
    RelationshipMetadataInDB
)
from .crud import table_metadata, field_metadata, relationship_metadata

# Crear el router SIN prefijo - importante!
router = APIRouter()

# Rutas para TableMetadata
@router.post("/tables/", response_model=TableMetadataInDB)
def create_table(
    table: TableMetadataCreate,
    db: Session = Depends(get_db)
):
    """Crear nueva tabla en metadata"""
    db_table = table_metadata.get_by_name(db, name=table.name)
    if db_table:
        raise HTTPException(
            status_code=400,
            detail=f"Table {table.name} already exists"
        )
    return table_metadata.create(db, obj_in=table)

@router.get("/tables/", response_model=List[TableMetadataInDB])
def read_tables(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Obtener lista de tablas"""
    return table_metadata.get_multi(db, skip=skip, limit=limit)

@router.get("/tables/{table_id}", response_model=TableMetadataInDB)
def read_table(table_id: int, db: Session = Depends(get_db)):
    """Obtener una tabla específica con sus campos"""
    db_table = table_metadata.get_with_fields(db, table_id)
    if db_table is None:
        raise HTTPException(
            status_code=404, 
            detail=f"Table with id {table_id} not found"
        )
    return db_table

@router.put("/tables/{table_id}", response_model=TableMetadataInDB)
def update_table(
    table_id: int,
    table: TableMetadataUpdate,
    db: Session = Depends(get_db)
):
    """Actualizar una tabla"""
    db_table = table_metadata.get(db, table_id)
    if db_table is None:
        raise HTTPException(status_code=404, detail="Table not found")
    return table_metadata.update(db, db_obj=db_table, obj_in=table)

@router.delete("/tables/{table_id}")
def delete_table(table_id: int, db: Session = Depends(get_db)):
    """Eliminar una tabla y sus relaciones"""
    try:
        # Verificar si la tabla existe
        db_table = table_metadata.get(db, id=table_id)
        if not db_table:
            raise HTTPException(
                status_code=404,
                detail=f"Table with id {table_id} not found"
            )
        
        # 1. Eliminar las relaciones donde esta tabla es origen o destino
        db.query(RelationshipMetadata).filter(
            (RelationshipMetadata.source_table_id == table_id) | 
            (RelationshipMetadata.target_table_id == table_id)
        ).delete(synchronize_session=False)
        
        # 2. Eliminar todos los campos de la tabla
        db.query(FieldMetadata).filter(
            FieldMetadata.table_id == table_id
        ).delete(synchronize_session=False)
        
        # 3. Finalmente eliminar la tabla
        db.query(TableMetadata).filter(
            TableMetadata.id == table_id
        ).delete(synchronize_session=False)
        
        # Commit de todas las eliminaciones
        db.commit()
        
        return JSONResponse(
            status_code=200,
            content={
                "message": f"Table {db_table.name} and all its relations deleted successfully",
                "id": table_id,
                "details": {
                    "table": db_table.name,
                    "display_name": db_table.display_name
                }
            }
        )
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting table: {str(e)}"
        )
        
@router.get("/tables/{table_id}/dependencies")
def get_table_dependencies(table_id: int, db: Session = Depends(get_db)):
    """Obtener las dependencias de una tabla antes de eliminarla"""
    try:
        # Verificar si la tabla existe
        db_table = table_metadata.get(db, id=table_id)
        if not db_table:
            raise HTTPException(
                status_code=404,
                detail=f"Table with id {table_id} not found"
            )
        
        # Obtener campos
        fields = db.query(FieldMetadata).filter(
            FieldMetadata.table_id == table_id
        ).all()
        
        # Obtener relaciones
        source_relations = db.query(RelationshipMetadata).filter(
            RelationshipMetadata.source_table_id == table_id
        ).all()
        
        target_relations = db.query(RelationshipMetadata).filter(
            RelationshipMetadata.target_table_id == table_id
        ).all()
        
        return {
            "table": {
                "id": db_table.id,
                "name": db_table.name,
                "display_name": db_table.display_name
            },
            "dependencies": {
                "fields": [
                    {
                        "id": field.id,
                        "name": field.name,
                        "display_name": field.display_name
                    } for field in fields
                ],
                "relations": {
                    "as_source": [
                        {
                            "id": rel.id,
                            "target_table_id": rel.target_table_id,
                            "relationship_type": rel.relationship_type
                        } for rel in source_relations
                    ],
                    "as_target": [
                        {
                            "id": rel.id,
                            "source_table_id": rel.source_table_id,
                            "relationship_type": rel.relationship_type
                        } for rel in target_relations
                    ]
                }
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting dependencies: {str(e)}"
        )

# Rutas para FieldMetadata
@router.post("/fields/", response_model=FieldMetadataInDB)
def create_field(
    field: FieldMetadataCreate,
    db: Session = Depends(get_db)
):
    """Crear nuevo campo"""
    db_table = table_metadata.get(db, field.table_id)
    if not db_table:
        raise HTTPException(
            status_code=404,
            detail=f"Table {field.table_id} not found"
        )
    return field_metadata.create(db, obj_in=field)

@router.get("/tables/{table_id}/fields/", response_model=List[FieldMetadataInDB])
def read_table_fields(
    table_id: int,
    db: Session = Depends(get_db)
):
    """Obtener todos los campos de una tabla"""
    return field_metadata.get_by_table(db, table_id)

@router.put("/fields/{field_id}", response_model=FieldMetadataInDB)
def update_field(
    field_id: int,
    field: FieldMetadataUpdate,
    db: Session = Depends(get_db)
):
    """Actualizar un campo"""
    db_field = field_metadata.get(db, field_id)
    if db_field is None:
        raise HTTPException(status_code=404, detail="Field not found")
    return field_metadata.update(db, db_obj=db_field, obj_in=field)

@router.delete("/fields/{field_id}")
def delete_field(field_id: int, db: Session = Depends(get_db)):
    """Eliminar un campo"""
    try:
        # Primero verificamos si el campo existe
        db_field = field_metadata.get(db, id=field_id)
        if not db_field:
            raise HTTPException(
                status_code=404,
                detail=f"Field with id {field_id} not found"
            )
            
        # Eliminamos el campo
        field_metadata.delete(db, id=field_id)
        
        return JSONResponse(
            status_code=200,
            content={
                "message": f"Field {db_field.name} deleted successfully",
                "id": field_id
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting field: {str(e)}"
        )
        
@router.post("/relationships/", response_model=RelationshipMetadataInDB)
def create_relationship(
    relationship: RelationshipMetadataCreate,
    db: Session = Depends(get_db)
):
    """Crear nueva relación entre tablas"""
    # Verificar que existan las tablas
    source_table = table_metadata.get(db, relationship.source_table_id)
    if not source_table:
        raise HTTPException(
            status_code=404,
            detail=f"Source table with id {relationship.source_table_id} not found"
        )
    
    target_table = table_metadata.get(db, relationship.target_table_id)
    if not target_table:
        raise HTTPException(
            status_code=404,
            detail=f"Target table with id {relationship.target_table_id} not found"
        )
    
    return relationship_metadata.create(db, obj_in=relationship)

@router.get("/relationships/", response_model=List[RelationshipMetadataInDB])
def read_relationships(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Obtener lista de relaciones"""
    return relationship_metadata.get_multi(db, skip=skip, limit=limit)

@router.get("/relationships/{relationship_id}", response_model=RelationshipMetadataInDB)
def read_relationship(relationship_id: int, db: Session = Depends(get_db)):
    """Obtener una relación específica"""
    db_relationship = relationship_metadata.get(db, relationship_id)
    if db_relationship is None:
        raise HTTPException(status_code=404, detail="Relationship not found")
    return db_relationship

@router.put("/relationships/{relationship_id}", response_model=RelationshipMetadataInDB)
def update_relationship(
    relationship_id: int,
    relationship: RelationshipMetadataUpdate,
    db: Session = Depends(get_db)
):
    """Actualizar una relación"""
    db_relationship = relationship_metadata.get(db, relationship_id)
    if db_relationship is None:
        raise HTTPException(status_code=404, detail="Relationship not found")
    return relationship_metadata.update(db, db_obj=db_relationship, obj_in=relationship)

@router.delete("/relationships/{relationship_id}", response_model=RelationshipMetadataInDB)
def delete_relationship(relationship_id: int, db: Session = Depends(get_db)):
    """Eliminar una relación"""
    return relationship_metadata.delete(db, id=relationship_id)

@router.get("/tables/{table_id}/relationships/", response_model=List[RelationshipMetadataInDB])
def read_table_relationships(
    table_id: int,
    db: Session = Depends(get_db)
):
    """Obtener todas las relaciones de una tabla (como fuente o destino)"""
    source_relations = relationship_metadata.get_by_source_table(db, table_id)
    target_relations = relationship_metadata.get_by_target_table(db, table_id)
    return source_relations + target_relations