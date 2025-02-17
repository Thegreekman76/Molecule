# backend\core\middleware\auth.py
from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from core.security.auth import SECRET_KEY, ALGORITHM
from typing import Optional
import jwt

security = HTTPBearer()

class AuthMiddleware:
    def __init__(self):
        self.security = HTTPBearer()

    async def __call__(self, request: Request) -> Optional[dict]:
        try:
            # Excluir rutas públicas
            if self.is_public_path(request.url.path):
                return None

            credentials: HTTPAuthorizationCredentials = await security(request)
            if not credentials:
                raise HTTPException(status_code=403, detail="Invalid authorization code.")

            token = credentials.credentials
            # Verificar y decodificar el token
            payload = jwt.decode(
                token, 
                SECRET_KEY, 
                algorithms=[ALGORITHM]
            )
            
            # Agregar información del usuario al request state
            request.state.user = payload
            return payload

        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token has expired")
        except jwt.JWTError:
            raise HTTPException(status_code=403, detail="Could not validate credentials")
        except Exception as e:
            raise HTTPException(status_code=403, detail=str(e))

    def is_public_path(self, path: str) -> bool:
        """Verificar si la ruta es pública"""
        public_paths = [
            "/docs",
            "/redoc",
            "/openapi.json",
            "/api/v1/auth/login",
            "/api/v1/auth/register",
            "/health",
            "/"
        ]
        return any(path.startswith(public_path) for public_path in public_paths)