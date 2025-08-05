#!/usr/bin/env python3
"""
Script de prueba para verificar la configuración del backend
"""

import sys
import subprocess
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_imports():
    """Probar que todas las dependencias se pueden importar"""
    required_modules = [
        'fastapi',
        'uvicorn',
        'pydantic',
        'openai',
        'pypdf',
        'multipart',
        'dotenv',
        'reportlab',
        'PIL',
        'httpx'
    ]
    
    logger.info("🧪 Probando importaciones...")
    
    for module in required_modules:
        try:
            __import__(module.replace('-', '_'))
            logger.info(f"✅ {module}")
        except ImportError as e:
            logger.error(f"❌ {module}: {e}")
            return False
    
    return True

def test_fastapi_app():
    """Probar que la aplicación FastAPI se puede crear"""
    try:
        logger.info("🧪 Probando creación de aplicación FastAPI...")
        from fastapi import FastAPI
        app = FastAPI()
        logger.info("✅ Aplicación FastAPI creada correctamente")
        return True
    except Exception as e:
        logger.error(f"❌ Error creando aplicación FastAPI: {e}")
        return False

def test_main_import():
    """Probar que main.py se puede importar"""
    try:
        logger.info("🧪 Probando importación de main.py...")
        import main
        logger.info("✅ main.py importado correctamente")
        return True
    except Exception as e:
        logger.error(f"❌ Error importando main.py: {e}")
        return False

def main():
    logger.info("🚀 Iniciando pruebas de configuración...")
    
    # Probar importaciones
    if not test_imports():
        logger.error("❌ Fallo en importaciones")
        sys.exit(1)
    
    # Probar FastAPI
    if not test_fastapi_app():
        logger.error("❌ Fallo en FastAPI")
        sys.exit(1)
    
    # Probar main.py
    if not test_main_import():
        logger.error("❌ Fallo en main.py")
        sys.exit(1)
    
    logger.info("✅ Todas las pruebas pasaron correctamente")
    logger.info("🎉 El backend está listo para funcionar")

if __name__ == "__main__":
    main() 