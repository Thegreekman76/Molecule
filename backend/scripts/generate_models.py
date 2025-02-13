# scripts/generate_models.py
import os
import sys
from pathlib import Path

# Agregar el directorio raíz del proyecto al PYTHONPATH
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

from core.generator.model_generator import ModelGenerator
from core.database.database import engine
import logging

def setup_directories():
    """Crear directorios necesarios si no existen"""
    directories = [
        'models/generated',
        'schemas/generated',
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        init_file = os.path.join(directory, '__init__.py')
        if not os.path.exists(init_file):
            with open(init_file, 'w') as f:
                f.write('# Generated files\n')

def generate_models(schema: str = 'public'):
    """Genera modelos y schemas desde la base de datos"""
    try:
        generator = ModelGenerator(engine)
        
        # Crear directorios
        setup_directories()
        
        # Obtener tablas
        tables = generator.get_tables(schema)
        logging.info(f"Found {len(tables)} tables to process")
        
        for table_name in tables:
            try:
                # Obtener información de la tabla
                table_info = generator.get_table_info(table_name, schema)
                
                # Generar y guardar modelo SQLAlchemy
                model_code = generator.generate_sqlalchemy_model(table_info)
                model_file = f'models/generated/{table_name}.py'
                with open(model_file, 'w') as f:
                    f.write(model_code)
                logging.info(f"Generated SQLAlchemy model: {model_file}")
                
                # Generar y guardar schema Pydantic
                schema_code = generator.generate_pydantic_schema(table_info)
                schema_file = f'schemas/generated/{table_name}.py'
                with open(schema_file, 'w') as f:
                    f.write(schema_code)
                logging.info(f"Generated Pydantic schema: {schema_file}")
                
            except Exception as e:
                logging.error(f"Error processing table {table_name}: {str(e)}")
                continue
        
        # Generar archivo __init__.py con imports
        generate_init_files(tables)
        
        logging.info("Model generation completed successfully")
        
    except Exception as e:
        logging.error(f"Error generating models: {str(e)}")
        raise

def generate_init_files(tables: list[str]):
    """Genera archivos __init__.py con imports"""
    # Para modelos SQLAlchemy
    with open('models/generated/__init__.py', 'w') as f:
        for table in tables:
            model_name = ''.join(word.capitalize() for word in table.split('_'))
            f.write(f'from .{table} import {model_name}\n')
        f.write('\n__all__ = [')
        f.write(', '.join(f"'{table}'" for table in tables))
        f.write(']\n')
    
    # Para schemas Pydantic
    with open('schemas/generated/__init__.py', 'w') as f:
        for table in tables:
            model_name = ''.join(word.capitalize() for word in table.split('_'))
            f.write(f'from .{table} import {model_name}Base, {model_name}Create, {model_name}Update, {model_name}InDB\n')

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    generate_models()