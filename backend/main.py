# main.py
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from core.database.database import get_db
from core.middleware.auth import AuthMiddleware
from api import api_router
from config.settings import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Framework for database-driven applications",
    version=settings.VERSION
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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

@app.get("/")
async def root():
    return {
        "message": f"{settings.PROJECT_NAME} API is running",
        "version": settings.VERSION
    }

@app.get("/health")
async def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, 
        host=settings.HOST,
        port=settings.PORT
    )