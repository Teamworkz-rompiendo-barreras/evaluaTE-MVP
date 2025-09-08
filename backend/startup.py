#!/usr/bin/env python3
"""
Archivo de inicio para Azure Web App
Este archivo es el punto de entrada principal que Azure usará para ejecutar la aplicación
"""
import os
import sys
from pathlib import Path

# Agregar el directorio actual al path de Python
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Importar y ejecutar la aplicación FastAPI
from main import app

# Configurar variables de entorno para Azure
os.environ.setdefault("HOST", "0.0.0.0")
os.environ.setdefault("PORT", "8080")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "8080")),
        reload=False,
        log_level="info"
    )
