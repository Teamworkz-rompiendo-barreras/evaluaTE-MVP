#!/usr/bin/env python3
"""
Script de inicio robusto para Azure Web App
"""

import os
import sys
import subprocess
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def install_dependencies():
    """Verificar dependencias sin instalar (más rápido para Azure)"""
    try:
        logger.info("🔧 Verificando dependencias...")
        
        # Solo verificar que las dependencias críticas estén disponibles
        try:
            import fastapi
            import uvicorn
            logger.info("✅ Dependencias ya instaladas")
            return True
        except ImportError as e:
            logger.error(f"❌ Dependencias faltantes: {e}")
            logger.error("❌ Las dependencias deben instalarse durante el despliegue, no al inicio")
            return False
                
    except Exception as e:
        logger.error(f"❌ Error verificando dependencias: {e}")
        return False

def check_dependencies():
    """Verificar que las dependencias estén instaladas (versión rápida)"""
    try:
        import fastapi
        import uvicorn
        logger.info("✅ Dependencias verificadas")
        return True
    except ImportError as e:
        logger.error(f"❌ Error importando dependencias: {e}")
        return False

def main():
    logger.info("🚀 Iniciando EvaluaTE Backend en Azure...")
    
    # Verificar dependencias rápidamente
    if not check_dependencies():
        logger.error("❌ Faltan dependencias críticas")
        sys.exit(1)
    
    # Obtener puerto de Azure (por defecto 8080)
    port = os.getenv('PORT', '8080')
    logger.info(f"🌐 Puerto: {port}")
    
    # Verificar que main.py existe
    if not os.path.exists('main.py'):
        logger.error("❌ No se encontró main.py")
        sys.exit(1)
    
    logger.info("✅ Configuración verificada")
    logger.info("🚀 Iniciando servidor FastAPI...")
    
    try:
        # Iniciar uvicorn con configuración optimizada para Azure
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "main:app", 
            "--host", "0.0.0.0", 
            "--port", port,
            "--log-level", "info",
            "--timeout-keep-alive", "300",
            "--timeout-graceful-shutdown", "60",
            "--workers", "1"
        ], check=True)
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Error iniciando servidor: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("🛑 Servidor detenido por el usuario")
        sys.exit(0)

if __name__ == "__main__":
    main() 