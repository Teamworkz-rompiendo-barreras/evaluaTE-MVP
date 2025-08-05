#!/usr/bin/env python3
"""
Script de inicio específico para Azure App Service
Configura el entorno y inicia el servidor correctamente
"""

import os
import sys
import logging
from pathlib import Path

# Configurar logging básico
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def setup_azure_environment():
    """Configura el entorno para Azure App Service"""
    logger.info("🔧 Configurando entorno para Azure App Service...")
    
    # Obtener puerto de Azure (por defecto 8000)
    port = int(os.getenv("PORT", "8000"))
    logger.info(f"🌐 Puerto configurado: {port}")
    
    # Configurar variables de entorno críticas
    required_vars = [
        "AZURE_OPENAI_API_KEY",
        "AZURE_OPENAI_ENDPOINT", 
        "AZURE_OPENAI_DEPLOYMENT",
        "AZURE_OPENAI_API_VERSION"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        logger.error(f"❌ Variables de entorno faltantes: {', '.join(missing_vars)}")
        logger.error("💡 Asegúrate de configurar estas variables en Azure App Service")
        return False
    
    logger.info("✅ Variables de entorno verificadas")
    
    # Configurar directorio de trabajo
    if os.getenv("WEBSITE_SITE_NAME"):
        logger.info(f"🏢 Sitio de Azure: {os.getenv('WEBSITE_SITE_NAME')}")
    
    # Configurar logging para Azure
    os.environ["LOG_LEVEL"] = "INFO"
    
    return True

def start_azure_server():
    """Inicia el servidor configurado para Azure"""
    try:
        import uvicorn
        
        # Configurar el servidor
        port = int(os.getenv("PORT", "8000"))
        host = "0.0.0.0"
        
        logger.info("🚀 Iniciando servidor EvaluaTE en Azure...")
        logger.info(f"📡 Host: {host}")
        logger.info(f"🌐 Puerto: {port}")
        logger.info(f"🔧 Entorno: {'PRODUCCIÓN' if os.getenv('PRODUCTION') else 'DESARROLLO'}")
        
        # Configuración optimizada para Azure
        uvicorn.run(
            "main:app",
            host=host,
            port=port,
            reload=False,  # Deshabilitar reload en producción
            log_level="info",
            timeout_keep_alive=120,
            timeout_graceful_shutdown=60,
            access_log=True,
            workers=1,  # Un solo worker para Azure App Service
            loop="asyncio"
        )
        
    except ImportError as e:
        logger.error(f"❌ Error al importar uvicorn: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Error al iniciar servidor: {e}")
        return False

if __name__ == "__main__":
    logger.info("🚀 Iniciando EvaluaTE Backend para Azure...")
    
    # Configurar entorno
    if not setup_azure_environment():
        logger.error("❌ Fallo en la configuración del entorno")
        sys.exit(1)
    
    # Iniciar servidor
    if not start_azure_server():
        logger.error("❌ Fallo al iniciar el servidor")
        sys.exit(1) 