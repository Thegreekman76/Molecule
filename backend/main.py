# main.py
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from core.database.database import get_db
from core.middleware.auth import AuthMiddleware
from api import api_router
import os

app = FastAPI(
    title="Molecule Framework",
    description="Framework for database-driven applications",
    version="0.1.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configura esto apropiadamente en producción
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
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "Molecule Framework API is running"}

@app.get("/health")
async def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, 
        host=os.getenv("HOST", "0.0.0.0"), 
        port=int(os.getenv("PORT", 8000))
    )