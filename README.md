# Localmente

## Backend

cd backend

source .venv/scripts/activate

uvicorn main:app --reload

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
| Detener Docker                       | `docker-compose down`                                                                                                                         |
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
