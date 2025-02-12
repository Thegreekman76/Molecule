# Este archivo implementa un sistema completo de autenticación y autorización que incluye:

## \* **Modelos y Schemas** :

- Modelos Pydantic para tokens y usuarios
- Modelo SQLAlchemy para la tabla de usuarios

## \* **Funcionalidades de Seguridad** :

- Hashing de contraseñas con bcrypt
- Generación y validación de tokens JWT
- Sistema de scopes para permisos

## \* **Gestión de Usuarios** :

- CRUD completo para usuarios
- Autenticación de usuarios
- Verificación de permisos

## \* **Decoradores y Dependencias** :

- Protección de rutas
- Verificación de scopes
- Obtención del usuario actual

# Ahora el sistema tiene:

1. Autenticación completa con JWT
2. Sistema de roles y permisos
3. Middleware de autenticación
4. Endpoints protegidos
5. Gestión de usuarios, roles y permisos
