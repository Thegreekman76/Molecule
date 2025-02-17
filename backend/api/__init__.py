# 
from fastapi import APIRouter
from .metadata.routes import router as metadata_router
from .auth.routes import router as auth_router

# Crear router principal
api_router = APIRouter()

# Incluir todos los sub-routers
api_router.include_router(auth_router, prefix="/auth", tags=["authentication"])
api_router.include_router(metadata_router, tags=["metadata"])  # Removido el prefix metadata