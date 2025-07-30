#!/usr/bin/env python3
"""
Script de startup para Azure Web App
Configura el entorno y ejecuta la aplicación FastAPI
"""

import os
import sys
import uvicorn
from pathlib import Path

def setup_environment():
    """Configura el entorno para Azure"""
    print("🔧 Configurando entorno para Azure...")
    
    # Configurar variables de entorno para Azure
    port = int(os.environ.get('PORT', 8000))
    host = os.environ.get('HOST', '0.0.0.0')
    
    print(f"📡 Puerto configurado: {port}")
    print(f"🌐 Host configurado: {host}")
    
    return host, port

def check_dependencies():
    """Verifica que las dependencias estén instaladas"""
    print("📦 Verificando dependencias...")
    
    required_packages = [
        'fastapi',
        'uvicorn',
        'openai',
        'pypdf',
        'pydantic',
        'python-dotenv'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} - FALTANTE")
    
    if missing_packages:
        print(f"\n❌ Faltan dependencias: {', '.join(missing_packages)}")
        print("Ejecuta: pip install -r requirements.txt")
        return False
    
    return True

def main():
    """Función principal"""
    print("🚀 Iniciando EvaluaTE Backend en Azure...")
    print("=" * 50)
    
    # Verificar dependencias
    if not check_dependencies():
        print("❌ Error: Faltan dependencias")
        sys.exit(1)
    
    # Configurar entorno
    host, port = setup_environment()
    
    print("\n✅ Todo configurado correctamente")
    print(f"🌐 Servidor iniciando en: http://{host}:{port}")
    print(f"📚 API Docs: http://{host}:{port}/docs")
    print(f"🔍 ReDoc: http://{host}:{port}/redoc")
    
    # Iniciar servidor
    try:
        uvicorn.run(
            "main:app",
            host=host,
            port=port,
            reload=False,  # Deshabilitar reload en producción
            log_level="info"
        )
    except Exception as e:
        print(f"❌ Error iniciando servidor: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 