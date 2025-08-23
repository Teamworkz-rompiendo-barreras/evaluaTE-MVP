#!/usr/bin/env python3
"""
Configuración específica para Azure App Service
Este archivo se ejecuta cuando Azure inicia la aplicación
"""
import os
import sys
from pathlib import Path

# Configurar el path de Python
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Configurar variables de entorno para Azure
os.environ.setdefault("HOST", "0.0.0.0")
os.environ.setdefault("PORT", "8000")
os.environ.setdefault("LOG_LEVEL", "INFO")

# Importar la aplicación FastAPI
from main import app

# Para Azure App Service, necesitamos exportar la app
application = app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "8000")),
        log_level=os.getenv("LOG_LEVEL", "info").lower()
    )
