# scripts/generate_tables.py
import os
import sys
from pathlib import Path

# Agregar el directorio raíz del proyecto al PYTHONPATH
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

from core.generator.table_generator import TableGenerator
from core.database.database import engine, SessionLocal
import logging

def generate_tables():
    """Genera las tablas físicas desde la metadata"""
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    print("\n🏗️  Iniciando generación de tablas físicas...")
    
    try:
        db = SessionLocal()
        generator = TableGenerator(engine)
        
        try:
            # Generar tablas
            created_tables = generator.generate_tables(db)
            
            if created_tables:
                print("\n✅ Tablas creadas exitosamente:")
                for table in created_tables:
                    print(f"  - {table}")
            else:
                print("\n⚠️  No se crearon nuevas tablas")
            
            print("\n🎉 Proceso completado!")
            
        except Exception as e:
            print(f"\n❌ Error durante la generación: {str(e)}")
        finally:
            db.close()
            
    except Exception as e:
        print(f"\n❌ Error de conexión: {str(e)}")

if __name__ == "__main__":
    generate_tables()