#!/usr/bin/env python3
"""
Script de inicio específico para Azure Web App
Configurado para funcionar de manera robusta en el entorno de Azure
"""
import os
import sys
from pathlib import Path

# Agregar el directorio actual al path de Python
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Configurar variables de entorno para Azure
os.environ.setdefault("HOST", "0.0.0.0")
os.environ.setdefault("PORT", "8080")

def main():
    """Función principal de inicio para Azure"""
    try:
        # Importar la aplicación FastAPI
        from main import app
        
        # Importar uvicorn
        import uvicorn
        
        # Configurar y ejecutar el servidor
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8080,
            log_level="info",
            access_log=True
        )
    except Exception as e:
        print(f"Error iniciando la aplicación: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
