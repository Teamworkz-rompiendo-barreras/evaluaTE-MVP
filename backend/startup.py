#!/usr/bin/env python3
"""
Script de startup para Azure Web App
Configura el entorno y ejecuta la aplicación FastAPI
"""

import os
import sys
import subprocess
from pathlib import Path

def check_environment():
    """Verifica que las variables de entorno críticas estén configuradas"""
    required_vars = [
        'AZURE_OPENAI_API_KEY',
        'AZURE_OPENAI_ENDPOINT', 
        'AZURE_OPENAI_DEPLOYMENT',
        'AZURE_OPENAI_API_VERSION'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ Variables de entorno faltantes:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\n⚠️ La aplicación funcionará en modo de prueba sin IA avanzada")
        print("Para funcionalidad completa, configura las variables en el archivo .env")
        return False
    
    print("✅ Variables de entorno críticas configuradas")
    return True

def check_dependencies():
    """Verifica que las dependencias estén instaladas"""
    required_packages = [
        'fastapi',
        'uvicorn',
        'pypdf',
        'openai'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Dependencias faltantes:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\nEjecuta: pip install -r requirements.txt")
        return False
    
    print("✅ Dependencias verificadas")
    return True

def main():
    print("🚀 Iniciando EvaluaTE Backend...")
    print("=" * 50)
    
    # Verificar entorno
    env_ok = check_environment()
    deps_ok = check_dependencies()
    
    if not deps_ok:
        print("❌ Error: Faltan dependencias")
        sys.exit(1)
    
    if not env_ok:
        print("⚠️ Advertencia: Variables de entorno no configuradas")
        print("La aplicación funcionará en modo de prueba")
    
    # Obtener puerto de la variable de entorno (Azure usa PORT=8080)
    port = os.getenv('PORT', '8000')
    print(f"🌐 Usando puerto: {port}")
    
    print("\n✅ Todo configurado correctamente")
    print("🚀 Iniciando servidor...")
    
    # Iniciar servidor
    try:
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "main:app", 
            "--host", "0.0.0.0", 
            "--port", port,
            "--reload"
        ], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error iniciando servidor: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 