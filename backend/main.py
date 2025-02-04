from fastapi import Depends, FastAPI, HTTPException
import os

from sqlalchemy import text
from core.database.database import get_db
from sqlalchemy.orm import Session

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Molecule Framework API is running"}

@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    try:
        # Ejecutar consulta simple de prueba
        result = db.execute(text("SELECT 1")).fetchone()
        return {
            "status": "ok",
            "database": "connected" if result[0] == 1 else "error"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Database connection failed!!: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, 
        host=os.getenv("HOST", "0.0.0.0"), 
        port=int(os.getenv("PORT", 8000))
    )