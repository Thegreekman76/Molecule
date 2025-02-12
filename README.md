# Localmente

## Backend

cd backend

source .venv/scripts/activate

uvicorn main:app --reload

### Alembic

#### Para futuras migraciones, cuando hagas cambios en los modelos:

- alembic revision --autogenerate -m "Descripción del cambio"
- alembic upgrade head

#### También puedes verificar el estado de las migraciones con:

- alembic current # Muestra la revisión actual
- alembic history # Muestra el historial de migraciones

## Frontend

cd frontend

source .venv/scripts/activate

reflex run --frontend-port 3000

# Docker

## Ejecutar

### Desde la raiz del proyecto

### **Comandos Útiles**

| Descripción                          | Comando                                                                                                                                       |
| ------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------- |
| Detener Docker                       | `docker-compose down -v`                                                                                                                      |
| Ver logs de PostgreSQL               | `docker logs molecule_db`                                                                                                                     |
| Reiniciar el servicio                | `docker-compose restart backend`                                                                                                              |
| Verificar el estado de los servicios | `docker-compose ps`                                                                                                                           |
| Reconstruir servicios                | `docker-compose up --build -d `                                                                                                               |
| Entrar al backend para debugear      | `docker exec -it molecule_backend bash`                                                                                                       |
| Monitorear logs en tiempo real       | `docker-compose logs -f backend `                                                                                                             |
| Entrar a la consola de PostgreSQL    | `docker exec -it molecule_db psql -U admin molecule_db`                                                                                       |
| Ejecutar                             | `docker-compose up -d`                                                                                                                        |
| Ver logs del Backen                  | `docker-compose logs backend`                                                                                                                 |
| Probar endpoints                     | `docker exec molecule_backend curl -s http://localhost:8000 `                                                                                 |
| Verificar coneccion postgres         | `docker exec -it molecule_backend bash -c "psql -U admin -h postgres -d molecule_db -c '\dt'"molecule_backend curl -s http://localhost:8000 ` |

### Limpiar todo completamente

docker system prune -af
docker volume prune -f
docker-compose down -v --remove-orphans

### Reconstruir con caché fresca

docker-compose up --force-recreate --build -d

# Estructura del proyecto Backend

backend/
|── alembic/ # Configuración y migraciones de Alembic
│ ├── versions/ # Archivos de migración
│ └── env.py # Configuración de entorno Alembic
├── core/ # Núcleo del framework
│ ├── database/
│ │ ├── **init**.py
│ │ ├── database.py # Configuración de base de datos (existente)
│ │ └── base.py # Clase base para modelos
│ ├── metadata/ # Sistema de metadatos
│ │ ├── **init**.py
│ │ ├── models.py # Modelos para metadatos
│ │ └── schema.py # Schemas Pydantic para metadatos
│ ├── generator/ # Generador automático
│ │ ├── **init**.py
│ │ ├── model_gen.py # Generador de modelos
│ │ └── api_gen.py # Generador de APIs
│ └── security/ # Seguridad y autenticación
│ ├── **init**.py
│ └── auth.py # Configuración de autenticación
├── api/ # APIs del framework
│ ├── **init**.py
│ ├── metadata/ # APIs para gestión de metadatos
│ │ ├── **init**.py
│ │ ├── routes.py
│ │ └── crud.py
│ └── crud/ # APIs CRUD generadas
│ ├── **init**.py
│ └── base.py
├── models/ # Modelos SQLAlchemy
│ ├── **init**.py
│ └── base.py
├── schemas/ # Schemas Pydantic
│ ├── **init**.py
│ └── base.py
├── utils/ # Utilidades
│ ├── **init**.py
│ └── helpers.py│
├── scripts/ # Scripts
│ ├── create_admin.py # crea el usuario ADMIN
│ └── seed_metadata.py # crea registros en tablas
├── config.py # Configuración global
├── main.py # Punto de entrada (existente)
├── requirements.txt # Dependencias (existente)
└── .env # Variables de entorno
