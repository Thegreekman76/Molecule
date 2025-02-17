# Documentación del Framework Molecule

## Información General

### Repositorio

El código fuente del framework está disponible en GitHub:

- URL: https://github.com/Thegreekman76/Molecule
- Branch principal: main

### Visión General

Molecule es un framework para desarrollo rápido de aplicaciones basadas en base de datos, que permite:

- Generación automática de modelos y APIs desde la base de datos
- Sistema de metadatos para describir tablas y relaciones
- Generación de interfaces de usuario basadas en templates
- Sistema completo de autenticación y autorización
- Gestión de roles y permisos

### Stack Tecnológico

- **Backend**:
  - FastAPI: Framework web
  - SQLAlchemy: ORM
  - Pydantic: Validación de datos
  - Alembic: Migraciones de base de datos
  - PostgreSQL: Base de datos
- **Frontend** (Planificado):
  - Reflex: Framework UI

## Estado Actual

### 1. Sistema de Base de Datos

#### 1.1 Configuración Base

- Conexión a PostgreSQL configurada
- Pooling de conexiones implementado
- Sistema de migraciones con Alembic

#### 1.2 Sistema de Metadatos

- Modelos para:
  - TableMetadata: Información de tablas
  - FieldMetadata: Información de campos
  - RelationshipMetadata: Relaciones entre tablas
  - UITemplate: Templates de interfaz

### 2. APIs

#### 2.1 Endpoints de Metadatos

- CRUD completo para:
  - Tablas
  - Campos
  - Relaciones
  - Templates UI

#### 2.2 Sistema de Autenticación

- JWT implementado
- Manejo de tokens
- Roles y permisos básicos

### 3. Generadores

#### 3.1 Generador de Tablas

- Creación de tablas físicas desde metadata
- Mapeo de tipos de datos
- Manejo de relaciones

#### 3.2 Generador de Modelos

- Generación de modelos SQLAlchemy
- Generación de schemas Pydantic
- Detección automática de relaciones

## Estructura del Proyecto

```
 backend/
├── alembic/                    # Configuración de migraciones
│   ├── versions/               # Archivos de migración
│   ├── env.py                  # Entorno de Alembic
│   └── script.py.mako          # Template de migraciones
│
├── api/                        # APIs del framework
│   ├── __init__.py             #
│   ├── crud/                   #
│   │   ├── __init__.py         #
│   │   └── base.py             #
│   ├── auth/                   # Autenticación
│   │   ├── routes.py           # Endpoints de auth
│   │   └── roles.py            # Manejo de roles
│   └── metadata/               # APIs de metadatos
│       ├── routes.py           # Endpoints de metadatos
│       └── crud.py             # Operaciones CRUD
│
├── config/                     #
│   ├── __init__.py             #
│   └── settings.py/            # Configuración
│
├── core/                       # Núcleo del framework
│   ├── database/               # Configuración DB
│   │   ├── database.py         # Conexión
│   │   └── base.py             # Modelos base
│   ├── errors/                 #
│   │   └── handlers.py         #
│   ├── metadata/               # Sistema de metadatos
│   │   ├── models.py           # Modelos
│   │   └── schema.py           # Schemas
│   ├── security/               # Seguridad
│   │   ├── auth.py             # Autenticación
│   │   ├── schema.py           # Schemas
│   │   └── roles.py            # Roles
│   ├── middleware/             #
│   │   └── auth.py             #
│   └── generator/              # Generadores
│       ├── api_gen.py          #
│       ├── model_gen.py        # Generador de modelos
│       ├── model_generator.py  #
│       └── table_gen.py        # Generador de tablas
│
├── logs/                       #
│   └── molecule.log            #
│
├── models/                     # Modelos generados
│   ├── __init__.py             #
│   ├── base.py                 #
│   └── generated/              # Modelos automáticos
│       └── __init__.py         #
│
├── schemas/                    # Schemas Pydantic
│   ├── __init__.py             #
│   ├── base.py                 #
│   └── generated/              # Schemas automáticos
│       └── __init__.py         #
│
├── scripts/                    # Scripts de utilidad
│   ├── __init__.py             #
│   ├── generate_models.py      # Generación de modelos
│   ├── seed_metadata.py        #
│   ├── cleanup_database.py     #
│   └── generate_tables.py      # Generación de tablas
│
├── utils/                      #
│   ├── __init__.py             #
│   └── helpers.py              #
│
├── .env                        # Variables de entorno
├── main.py                     # Punto de entrada
└── requirements.txt            # Dependencias
```

## Componentes Principales

### 1. Archivos Core

#### 1.1 main.py

- Punto de entrada de la aplicación
- Configuración de FastAPI
- Middleware y CORS
- Registro de rutas

#### 1.2 config.py

- Configuraciones globales
- Variables de entorno
- Settings por ambiente

### 2. Sistema de Metadatos

#### 2.1 models.py

- TableMetadata
  - Define estructura de tablas
  - Configuración UI
  - Schema y visibilidad
- FieldMetadata
  - Tipos de campos
  - Validaciones
  - UI específica
- RelationshipMetadata
  - Tipos de relaciones
  - Claves foráneas
  - Cardinalidad

### 3. Sistema de Autenticación

#### 3.1 auth.py

- JWT Tokens
- Password hashing
- Roles y permisos
- Middleware de autenticación

## Pendiente de Implementación

### 1. Frontend

- Implementación con Reflex
- Templates UI
- Componentes reutilizables
- Sistema de formularios

### 2. Caché y Optimización

- Sistema de caché
- Optimización de queries
- Lazy loading
- Batch operations

### 3. Validaciones Avanzadas

- Validaciones personalizadas
- Reglas de negocio
- Triggers
- Computed fields

### 4. Reportes y Análisis

- Sistema de reportes
- Exportación de datos
- Dashboard
- Analytics

### 5. Sistema de Archivos

- Upload de archivos
- Procesamiento
- Almacenamiento
- CDN integration

### 6. Workflows

- Definición de flujos
- Estados y transiciones
- Acciones automáticas
- Notificaciones

## Guía de Desarrollo

### 1. Configuración Inicial

```bash
# Clonar repositorio
git clone https://github.com/Thegreekman76/Molecule.git
cd Molecule

# Crear entorno virtual
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
```

### 2. Base de Datos|

```bash
# Crear base de datos
createdb molecule_db

# Ejecutar migraciones
alembic upgrade head

# Crear e iniciar datos principales en la base de datos
python scripts/cleanup_database.py
```

### 3. Desarrollo

```bash
# Iniciar servidor
uvicorn main:app --reload

# Generar modelos
python scripts/generate_models.py

# Generar tablas
python scripts/generate_tables.py
```

## Notas de Implementación

### 1. Base de Datos

- Usar PostgreSQL 12 o superior
- Configurar pooling apropiadamente
- Mantener índices actualizados

### 2. Seguridad

- Cambiar SECRET_KEY en producción
- Implementar rate limiting
- Configurar CORS apropiadamente
- Usar HTTPS en producción

### 3. Desarrollo

- Seguir PEP 8
- Documentar código nuevo
- Mantener tests actualizados
- Usar tipos estáticos

## Cómo Continuar el Desarrollo

1. Revisar issues en GitHub
2. Seguir el roadmap de implementación
3. Mantener la documentación actualizada
4. Contribuir con mejoras y fixes
