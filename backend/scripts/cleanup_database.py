#!/usr/bin/env python
from sqlalchemy import create_engine, text, MetaData
from sqlalchemy.engine import URL
import os
from dotenv import load_dotenv
from passlib.context import CryptContext

# Configurar el contexto de encriptación
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_database_url():
    load_dotenv()
    return URL.create(
        drivername="postgresql",
        username=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        database=os.getenv("DB_NAME")
    )

def table_exists(connection, table_name):
    exists_query = text("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_name = :table_name
            AND table_schema = 'public'
        );
    """)
    return connection.execute(exists_query, {"table_name": table_name}).scalar()

def cleanup_and_init_database():
    # Crear engine
    engine = create_engine(get_database_url())
    
    with engine.connect() as connection:
        with connection.begin():
            print("\n=== Iniciando limpieza y configuración de la base de datos ===\n")
            
            # 1. Obtener todas las tablas existentes
            metadata = MetaData()
            metadata.reflect(bind=engine)
            
            # 2. Definir tablas del sistema que no deben eliminarse
            system_tables = {
                'alembic_version',
                'users',
                'roles',
                'permissions',
                'table_metadata',
                'field_metadata',
                'relationship_metadata',
                'ui_templates',
                'user_roles'
            }
            
            # 3. Eliminar tablas que no son del sistema
            print("Eliminando tablas generadas...")
            for table in reversed(metadata.sorted_tables):
                if table.name not in system_tables:
                    print(f"Eliminando tabla: {table.name}")
                    connection.execute(text(f"DROP TABLE IF EXISTS {table.name} CASCADE;"))
            
            # 4. Limpiar datos de las tablas del sistema
            print("\nLimpiando datos de las tablas del sistema...")
            metadata_tables = [
                'relationship_metadata',
                'field_metadata',
                'table_metadata',
                'ui_templates'
            ]
            
            for table in metadata_tables:
                if table_exists(connection, table):
                    print(f"Limpiando tabla: {table}")
                    connection.execute(text(f"TRUNCATE TABLE {table} CASCADE;"))
            
            # 5. Recrear tabla user_roles si no existe
            print("\nVerificando tabla user_roles...")
            connection.execute(text("""
                DROP TABLE IF EXISTS user_roles CASCADE;
                CREATE TABLE user_roles (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    role_id INTEGER NOT NULL,
                    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
                    FOREIGN KEY (role_id) REFERENCES roles (id) ON DELETE CASCADE,
                    UNIQUE(user_id, role_id)
                );
            """))
            
            # 6. Limpiar y configurar roles y permisos
            print("\nConfigurando roles y permisos...")
            connection.execute(text("TRUNCATE TABLE permissions CASCADE;"))
            connection.execute(text("TRUNCATE TABLE roles CASCADE;"))
            connection.execute(text("TRUNCATE TABLE users CASCADE;"))
            
            # 7. Crear rol admin
            print("Creando rol admin...")
            result = connection.execute(text("""
                INSERT INTO roles (name, description, is_active)
                VALUES ('admin', 'Administrator role', true)
                RETURNING id;
            """))
            admin_role_id = result.scalar()
            
            # 8. Crear permisos básicos
            print("Creando permisos básicos...")
            basic_permissions = [
                ("users:manage", "Gestión completa de usuarios", "users", "manage"),
                ("roles:manage", "Gestión completa de roles", "roles", "manage"),
                ("metadata:manage", "Gestión completa de metadatos", "metadata", "manage"),
                ("templates:manage", "Gestión completa de templates", "templates", "manage"),
                ("system:manage", "Gestión del sistema", "system", "manage")
            ]
            
            for name, description, resource, action in basic_permissions:
                connection.execute(
                    text("""
                        INSERT INTO permissions (name, description, resource, action)
                        VALUES (:name, :description, :resource, :action)
                    """),
                    {
                        "name": name,
                        "description": description,
                        "resource": resource,
                        "action": action
                    }
                )
            
            # 9. Crear usuario admin
            print("\nCreando usuario admin...")
            admin_password = "admin123"  # Contraseña por defecto
            hashed_password = pwd_context.hash(admin_password)
            
            result = connection.execute(text("""
                INSERT INTO users (
                    username, email, full_name, hashed_password, 
                    is_active, is_superuser
                )
                VALUES (
                    'admin', 'admin@example.com', 'Administrator',
                    :hashed_password, true, true
                )
                RETURNING id;
            """), {"hashed_password": hashed_password})
            
            admin_user_id = result.scalar()
            
            # 10. Asignar rol admin al usuario admin
            print("Asignando rol admin al usuario admin...")
            connection.execute(text("""
                INSERT INTO user_roles (user_id, role_id)
                VALUES (:user_id, :role_id)
            """), {"user_id": admin_user_id, "role_id": admin_role_id})
            
            print("\n=== Configuración completada exitosamente ===")
            print("\nCredenciales por defecto:")
            print("Username: admin")
            print("Password: admin123")
            print("\nPor favor, cambia la contraseña después de iniciar sesión.")

if __name__ == "__main__":
    try:
        cleanup_and_init_database()
    except Exception as e:
        print(f"\nError durante la configuración: {str(e)}")