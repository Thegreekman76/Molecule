#!/bin/bash

# Crear estructura de carpetas
mkdir -p \
  backend/core/{database,api} \
  frontend/{core/components,assets} \
  docker \
  .github/workflows

# Archivo .env para backend
cat > backend/.env <<EOL
POSTGRES_USER=admin
POSTGRES_PASSWORD=secret
POSTGRES_DB=molecule_db
DATABASE_URL=postgresql://admin:secret@localhost:5432/molecule_db
EOL

# Docker-compose.yml
cat > docker-compose.yml <<EOL
version: '3.8'

services:
  postgres:
    image: postgres:16
    container_name: molecule_db
    environment:
      POSTGRES_USER: admin
      POSTGRES_PASSWORD: secret
      POSTGRES_DB: molecule_db
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    networks:
      - molecule_net

  pgadmin:
    image: dpage/pgadmin4:7.8
    container_name: molecule_pgadmin
    environment:
      PGADMIN_DEFAULT_EMAIL: admin@molecule.com
      PGADMIN_DEFAULT_PASSWORD: secret
    ports:
      - "5050:80"
    depends_on:
      - postgres
    networks:
      - molecule_net

  backend:
    build:
      context: ./backend
      dockerfile: ../docker/backend.Dockerfile
    container_name: molecule_backend
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://admin:secret@postgres:5432/molecule_db
    depends_on:
      - postgres
    volumes:
      - ./backend:/app
      - ./backend/env:/app/env  # Solo para desarrollo
    networks:
      - molecule_net

volumes:
  postgres_data:

networks:
  molecule_net:
    driver: bridge
EOL

# Backend Dockerfile
cat > docker/backend.Dockerfile <<EOL
FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install --upgrade pip

WORKDIR /backend
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
EOL

# Backend requirements
cat > backend/requirements.txt <<EOL
fastapi>=0.110.0
uvicorn>=0.29.0
sqlalchemy>=2.0.28
pydantic>=2.6.1
python-dotenv>=1.0.0
psycopg2-binary>=2.9.9
alembic>=1.13.1
EOL

# Frontend requirements
cat > frontend/requirements.txt <<EOL
reflex>=0.4.9
python-dotenv>=1.0.0
EOL

# Frontend app.py
cat > frontend/app.py <<EOL
import reflex as rx

config = rx.Config(
    app_name="frontend_web",
    frontend_port=3000,
    api_port=8000,
    backend_port=8000
)

class State(rx.State):
    pass

def index():
    return rx.center(
        rx.vstack(
            rx.heading("Welcome to Molecule Framework!", size="9"),
            rx.text("Start building your application"),
            spacing="4",
        ),
        height="100vh",
    )

app = rx.App()
app.add_page(index, route="/")
EOL

# Crear entornos virtuales
cd backend && python -m venv .venv && cd ..
cd frontend && python -m venv .venv && cd ..

# Permisos de ejecución
chmod +x backend/start.sh
chmod +x frontend/start.sh

# Crear .gitignore
cat > .gitignore <<EOL
.env
**/env/
**/__pycache__/
*.pyc
*.pyo
*.pyd
.DS_Store
*.sqlite3
/docker/.env
/postgres_data
EOL

echo "✅ Estructura creada exitosamente!"
echo "👉 Pasos siguientes:"
echo "1. Configurar Docker: docker-compose up -d"
echo "2. Activar entorno backend: cd backend && source .venv/scripts/activate && pip install -r requirements.txt"
echo "3. Activar entorno frontend: cd frontend && source .venv/scripts/activate && pip install -r requirements.txt"
echo "4. Iniciar frontend: reflex run"