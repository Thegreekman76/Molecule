# main.py
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from core.database.database import get_db
from core.middleware.auth import AuthMiddleware
from api import api_router
from config.settings import settings
import logging

# Obtener logger para este módulo
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Framework for database-driven applications",
    version=settings.VERSION
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)

# Agregar middleware de autenticación
auth_middleware = AuthMiddleware()

@app.middleware("http")
async def authentication_middleware(request: Request, call_next):
    await auth_middleware(request)
    response = await call_next(request)
    return response

# Incluir todas las rutas de la API
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.on_event("startup")
async def startup_event():
    logger.info("Starting up Molecule Framework")
    logger.info(f"Debug mode: {settings.DEBUG}")
    logger.info(f"Environment: Development")
    logger.info(f"API Version: {settings.VERSION}")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down Molecule Framework")

@app.get("/")
async def root():
    logger.info("Root endpoint called")
    return {"message": f"{settings.PROJECT_NAME} API is running"}

@app.get("/health")
async def health_check():
    logger.info("Health check endpoint called")
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting server...")
    uvicorn.run(
        app, 
        host=settings.HOST, 
        port=settings.PORT
    )