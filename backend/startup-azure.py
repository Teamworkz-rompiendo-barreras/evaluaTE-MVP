#!/usr/bin/env python3
"""
Archivo de inicio optimizado para Azure Web App
Este archivo maneja la configuración específica de Azure y el arranque de la aplicación
"""
import os
import sys
import time
import logging
from pathlib import Path

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def log(level: str, msg: str) -> None:
    """Función de logging con timestamp"""
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"{ts} - {level} - {msg}")
    sys.stdout.flush()

def ensure_utf8() -> None:
    """Asegurar configuración UTF-8"""
    os.environ.setdefault("PYTHONIOENCODING", "utf-8")
    os.environ.setdefault("LC_ALL", "C.UTF-8")
    os.environ.setdefault("LANG", "C.UTF-8")
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8")
        if hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

def setup_environment() -> None:
    """Configurar variables de entorno para Azure"""
    # Variables de entorno por defecto
    os.environ.setdefault("HOST", "0.0.0.0")
    os.environ.setdefault("PORT", "8000")
    os.environ.setdefault("LOG_LEVEL", "INFO")
    
    # Limpiar proxies heredados
    for var in ("HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY"):
        if var in os.environ:
            del os.environ[var]
    
    # Configurar encoding
    ensure_utf8()

def run_application() -> None:
    """Ejecutar la aplicación FastAPI"""
    try:
        # Agregar el directorio actual al path
        current_dir = Path(__file__).parent
        sys.path.insert(0, str(current_dir))
        
        # Importar la aplicación
        from main import app
        
        # Configurar host y puerto
        host = os.getenv("HOST", "0.0.0.0")
        port = int(os.getenv("PORT", "8000"))
        
        logger.info(f"🚀 Iniciando EvaluaTE Backend en {host}:{port}")
        
        # Importar uvicorn y ejecutar
        import uvicorn
        uvicorn.run(
            app,
            host=host,
            port=port,
            log_level=os.getenv("LOG_LEVEL", "info").lower(),
            access_log=True
        )
        
    except ImportError as e:
        logger.error(f"❌ Error importando la aplicación: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Error ejecutando la aplicación: {e}")
        sys.exit(1)

def main() -> None:
    """Función principal"""
    log("INFO", "🚀 Iniciando EvaluaTE Backend en Azure...")
    
    # Configurar entorno
    setup_environment()
    log("INFO", "✅ Configuración del entorno completada")
    
    # Ejecutar aplicación
    run_application()

if __name__ == "__main__":
    main()


