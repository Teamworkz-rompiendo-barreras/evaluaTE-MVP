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
    """Instalar dependencias si no están disponibles"""
    try:
        logger.info("🔧 Verificando dependencias...")
        
        # Intentar importar dependencias críticas
        try:
            import fastapi
            import uvicorn
            logger.info("✅ Dependencias ya instaladas")
            return True
        except ImportError:
            logger.info("📦 Instalando dependencias...")
            
            # Determinar qué archivo de requirements usar
            requirements_file = 'requirements-azure.txt' if os.path.exists('requirements-azure.txt') else 'requirements.txt'
            
            # Instalar dependencias
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", "-r", requirements_file
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info("✅ Dependencias instaladas correctamente")
                return True
            else:
                logger.error(f"❌ Error instalando dependencias: {result.stderr}")
                return False
                
    except Exception as e:
        logger.error(f"❌ Error en instalación de dependencias: {e}")
        return False

def check_dependencies():
    """Verificar que las dependencias estén instaladas"""
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
    
    # Instalar dependencias si es necesario
    if not install_dependencies():
        logger.error("❌ No se pudieron instalar las dependencias")
        sys.exit(1)
    
    # Verificar dependencias después de la instalación
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
        # Iniciar uvicorn con configuración robusta
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "main:app", 
            "--host", "0.0.0.0", 
            "--port", port,
            "--log-level", "info",
            "--timeout-keep-alive", "120"
        ], check=True)
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Error iniciando servidor: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("🛑 Servidor detenido por el usuario")
        sys.exit(0)

if __name__ == "__main__":
    main() 