# scripts/create_admin.py
import os
import sys
from pathlib import Path

# Agregar el directorio raíz del proyecto al PYTHONPATH
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

from core.database.database import SessionLocal
from core.security.auth import UserModel, pwd_context
from core.security.roles import Role, Permission
from sqlalchemy.exc import IntegrityError

def get_or_create(db, model, **kwargs):
    """Obtener o crear una instancia del modelo"""
    instance = db.query(model).filter_by(**kwargs).first()
    if instance:
        return instance, False
    
    instance = model(**kwargs)
    try:
        db.add(instance)
        db.commit()
        db.refresh(instance)
        return instance, True
    except IntegrityError:
        db.rollback()
        instance = db.query(model).filter_by(**kwargs).first()
        return instance, False

def create_initial_admin():
    db = SessionLocal()
    try:
        # Verificar si el usuario admin ya existe
        admin_user = db.query(UserModel).filter(UserModel.username == "admin").first()
        if admin_user:
            print("⚠️  El usuario admin ya existe")
            return

        print("🔧 Configurando roles y permisos...")
        
        # Crear o obtener rol de administrador
        admin_role, created = get_or_create(
            db, 
            Role,
            name="admin",
            description="Administrador del sistema"
        )
        if created:
            print("✅ Rol de administrador creado")
        else:
            print("ℹ️  Usando rol de administrador existente")

        # Crear o obtener permiso de acceso total
        all_access, created = get_or_create(
            db,
            Permission,
            name="all_access",
            description="Acceso total al sistema",
            resource="*",
            action="*"
        )
        if created:
            print("✅ Permiso de acceso total creado")
        else:
            print("ℹ️  Usando permiso de acceso total existente")

        # Asignar permisos al rol admin si no los tiene
        if all_access not in admin_role.permissions:
            admin_role.permissions.append(all_access)
            db.commit()
            print("✅ Permisos asignados al rol de administrador")

        print("👤 Creando usuario administrador...")
        
        # Datos del usuario admin
        admin_data = {
            "username": "admin",
            "email": "admin@molecule.com",
            "password": "admin123",
            "full_name": "Administrator",
            "is_superuser": True
        }

        # Crear el usuario
        hashed_password = pwd_context.hash(admin_data["password"])
        admin_user = UserModel(
            username=admin_data["username"],
            email=admin_data["email"],
            full_name=admin_data["full_name"],
            hashed_password=hashed_password,
            is_superuser=admin_data["is_superuser"],
            is_active=True
        )
        
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)

        # Asignar rol de admin
        admin_user.roles.append(admin_role)
        db.commit()

        print("\n✅ Configuración completada exitosamente")
        print("----------------------------------------")
        print("Usuario administrador creado:")
        print(f"Username: {admin_data['username']}")
        print(f"Password: {admin_data['password']}")
        print("----------------------------------------")

    except Exception as e:
        print(f"❌ Error en la configuración: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_initial_admin()