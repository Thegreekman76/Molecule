# backend\scripts\seed_metadata.py
import sys
import os
from pathlib import Path

# Agregar el directorio raíz del proyecto al PYTHONPATH
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

from core.database.database import SessionLocal
from core.metadata.models import TableMetadata, FieldMetadata, RelationshipMetadata
from sqlalchemy.exc import IntegrityError

def seed_metadata():
    db = SessionLocal()
    try:
        print("🌱 Iniciando la carga de datos de prueba...")

        # 1. Crear tablas de ejemplo
        print("\n📊 Creando tablas de metadata...")
        
        # Tabla Clientes
        customers_table = TableMetadata(
            name="customers",
            display_name="Clientes",
            description="Tabla de clientes del sistema",
            db_schema="public",
            is_visible=True,
            ui_settings={
                "icon": "users",
                "color": "blue",
                "list_display": ["id", "name", "email", "phone"]
            }
        )
        db.add(customers_table)
        db.commit()
        db.refresh(customers_table)
        print("✅ Tabla 'customers' creada")

        # Tabla Productos
        products_table = TableMetadata(
            name="products",
            display_name="Productos",
            description="Catálogo de productos",
            db_schema="public",
            is_visible=True,
            ui_settings={
                "icon": "box",
                "color": "green",
                "list_display": ["id", "name", "price", "stock"]
            }
        )
        db.add(products_table)
        db.commit()
        db.refresh(products_table)
        print("✅ Tabla 'products' creada")

        # 2. Crear campos para las tablas
        print("\n📋 Creando campos para las tablas...")
        
        # Campos para Clientes
        customer_fields = [
            FieldMetadata(
                table_id=customers_table.id,
                name="name",
                display_name="Nombre",
                field_type="string",
                length=100,
                is_nullable=False,
                ui_settings={
                    "widget": "text",
                    "placeholder": "Nombre del cliente",
                    "help_text": "Ingrese el nombre completo del cliente"
                }
            ),
            FieldMetadata(
                table_id=customers_table.id,
                name="email",
                display_name="Email",
                field_type="string",
                length=150,
                is_nullable=False,
                is_unique=True,
                ui_settings={
                    "widget": "email",
                    "placeholder": "email@ejemplo.com"
                }
            ),
            FieldMetadata(
                table_id=customers_table.id,
                name="phone",
                display_name="Teléfono",
                field_type="string",
                length=20,
                is_nullable=True,
                ui_settings={
                    "widget": "phone",
                    "placeholder": "+XX XXX-XXXXXXX"
                }
            )
        ]
        db.bulk_save_objects(customer_fields)
        db.commit()
        print("✅ Campos para 'customers' creados")

        # Campos para Productos
        product_fields = [
            FieldMetadata(
                table_id=products_table.id,
                name="name",
                display_name="Nombre",
                field_type="string",
                length=200,
                is_nullable=False,
                ui_settings={
                    "widget": "text",
                    "placeholder": "Nombre del producto"
                }
            ),
            FieldMetadata(
                table_id=products_table.id,
                name="description",
                display_name="Descripción",
                field_type="text",
                is_nullable=True,
                ui_settings={
                    "widget": "textarea",
                    "rows": 4
                }
            ),
            FieldMetadata(
                table_id=products_table.id,
                name="price",
                display_name="Precio",
                field_type="float",
                is_nullable=False,
                ui_settings={
                    "widget": "number",
                    "min": 0,
                    "step": 0.01,
                    "currency": "USD"
                }
            ),
            FieldMetadata(
                table_id=products_table.id,
                name="stock",
                display_name="Stock",
                field_type="integer",
                is_nullable=False,
                default_value="0",
                ui_settings={
                    "widget": "number",
                    "min": 0
                }
            )
        ]
        db.bulk_save_objects(product_fields)
        db.commit()
        print("✅ Campos para 'products' creados")

        # 3. Crear algunas relaciones
        print("\n🔗 Creando relaciones entre tablas...")
        
        # Relación de Órdenes (se creará después) con Clientes
        relationship = RelationshipMetadata(
            source_table_id=customers_table.id,
            target_table_id=products_table.id,
            relationship_type="ManyToMany",
            source_field="customer_id",
            target_field="product_id"
        )
        db.add(relationship)
        db.commit()
        print("✅ Relación Clientes-Productos creada")

        print("\n✨ Datos de prueba cargados exitosamente!")

    except IntegrityError as e:
        print(f"\n❌ Error de integridad en la base de datos: {str(e)}")
        db.rollback()
    except Exception as e:
        print(f"\n❌ Error inesperado: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_metadata()