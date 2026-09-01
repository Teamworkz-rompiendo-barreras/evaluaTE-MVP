# backend/auth.py
"""
Capa de Seguridad e Identidad.
Emisión y validación de tokens JWT mediante infraestructura Timezone-Aware.
"""
import os
import jwt
import logging
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

try:
    from backend.env_loader import load_backend_env
except ImportError:
    from env_loader import load_backend_env

load_backend_env()
logger = logging.getLogger(__name__)

security = HTTPBearer()

# RESOLUCIÓN CRÍTICA: Eliminación del secreto en código (Patrón Fail-Fast)
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    logger.critical("FATAL: SECRET_KEY no está definida en las variables de entorno.")
    raise ValueError("FATAL: El servidor no puede arrancar. Falta la SECRET_KEY de producción.")

ALGORITHM = "HS256"

def create_access_token(data: dict) -> str:
    """Genera un JWT firmado criptográficamente válido por 2 horas (Timezone-aware)."""
    to_encode = data.copy()
    
    # RESOLUCIÓN CRÍTICA: Uso de timezone.utc para evitar discrepancias de reloj en servidores Linux
    expire = datetime.now(timezone.utc) + timedelta(hours=2)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """Valida el JWT, verifica expiración matemática y extrae el ID del usuario de forma segura."""
    token = credentials.credentials
    try:
        # La librería PyJWT verifica automáticamente la clave 'exp' contra la hora UTC actual
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido: Ausencia de identificador de usuario.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user_id
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sesión expirada. Por favor, inicia sesión de nuevo.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas o manipuladas.",
            headers={"WWW-Authenticate": "Bearer"},
        )