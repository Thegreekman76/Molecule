# main.py
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from core.database.database import get_db
from core.middleware.auth import AuthMiddleware
from api import api_router
from config.settings import settings
from core.generator.api_gen import APIGenerator
from core.metadata.models import TableMetadata
from core.database.database import SessionLocal
from importlib import import_module
import logging
import traceback
import sys

def custom_excepthook(type, value, tb):
    print("=" * 80)
    print("EXCEPCIÓN DETALLADA:")
    print("-" * 80)
    traceback.print_exception(type, value, tb)
    print("=" * 80)

sys.excepthook = custom_excepthook



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

# Incluir todas las rutas de la API base
app.include_router(api_router, prefix=settings.API_V1_STR)

# Generar y registrar routers dinámicos
api_generator = APIGenerator()

def register_dynamic_routers():
    """Registra los routers generados dinámicamente desde los metadatos"""
    db = SessionLocal()
    try:
        tables = db.query(TableMetadata).all()
        
        for table in tables:
            try:
                print(f"\nProcesando tabla: {table.name}")
                module_path = f"models.generated.{table.name}"
                print(f"Intentando importar módulo: {module_path}")
                
                module = import_module(module_path)
                print(f"Módulo importado exitosamente")
                
                # Usar la función de capitalización correcta
                class_name = ''.join(word.capitalize() for word in table.name.split('_'))
                model = getattr(module, class_name)
                print(f"Modelo obtenido: {model}")
                
                # Generar router para la tabla
                router = api_generator.generate_router(table, model)
                
                # Registrar el router
                app.include_router(
                    router,
                    prefix=f"{settings.API_V1_STR}/{table.name}",
                    tags=[table.name]
                )
                logger.info(f"✅ Router generado para tabla: {table.name}")
                
            except Exception as e:
                print("\nError detallado al procesar {table.name}:")
                traceback.print_exc()
                logger.error(f"❌ Error generando router para {table.name}: {str(e)}")
                continue
                
    except Exception as e:
        print("\nError detallado en register_dynamic_routers:")
        traceback.print_exc()
        logger.error(f"Error registrando routers dinámicos: {str(e)}")
    finally:
        db.close()
        
@app.on_event("startup")
async def startup_event():
    logger.info("Starting up Molecule Framework")
    logger.info(f"Debug mode: {settings.DEBUG}")
    logger.info(f"Environment: Development")
    logger.info(f"API Version: {settings.VERSION}")
    # Registrar routers dinámicos al inicio
    register_dynamic_routers()

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down Molecule Framework")

@app.get("/")
async def root():
    return {"message": f"{settings.PROJECT_NAME} API is running"}

@app.get("/health")
async def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.HOST, port=settings.PORT)