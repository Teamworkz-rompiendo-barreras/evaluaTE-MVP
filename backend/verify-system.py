#!/usr/bin/env python3
"""
Script para verificar que el sistema backend esté funcionando correctamente
"""

import os
import sys
import importlib
from pathlib import Path

def check_python_version():
    """Verifica la versión de Python"""
    print("🐍 Verificando versión de Python...")
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - Compatible")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} - Requiere Python 3.8+")
        return False

def check_dependencies():
    """Verifica las dependencias principales"""
    print("\n📦 Verificando dependencias...")
    
    required_packages = [
        "fastapi",
        "uvicorn",
        "pydantic",
        "reportlab",
        "openai"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            importlib.import_module(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - No instalado")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️  Paquetes faltantes: {', '.join(missing_packages)}")
        print("Ejecuta: pip install -r requirements.txt")
        return False
    
    return True

def check_environment():
    """Verifica la configuración del entorno"""
    print("\n🔧 Verificando configuración del entorno...")
    
    # Verificar archivo .env
    env_file = Path(".env")
    if env_file.exists():
        print("✅ Archivo .env encontrado")
        
        # Leer variables críticas
        from dotenv import load_dotenv
        load_dotenv()
        
        critical_vars = [
            "AZURE_OPENAI_API_KEY",
            "AZURE_OPENAI_ENDPOINT",
            "AZURE_OPENAI_DEPLOYMENT"
        ]
        
        missing_vars = []
        for var in critical_vars:
            value = os.getenv(var)
            if value and value != "tu_api_key_aqui":
                print(f"✅ {var} configurada")
            else:
                print(f"❌ {var} no configurada")
                missing_vars.append(var)
        
        if missing_vars:
            print(f"\n⚠️  Variables críticas faltantes: {', '.join(missing_vars)}")
            print("Edita el archivo .env con tus credenciales de Azure")
            return False
    else:
        print("❌ Archivo .env no encontrado")
        print("Ejecuta: python setup-env.py")
        return False
    
    return True

def check_modules():
    """Verifica que los módulos principales se puedan importar"""
    print("\n🔍 Verificando módulos principales...")
    
    modules = [
        "main",
        "new_report_schema",
        "generate_report",
        "pdf_service",
        "document_intelligence"
    ]
    
    failed_modules = []
    
    for module in modules:
        try:
            importlib.import_module(module)
            print(f"✅ {module}")
        except Exception as e:
            print(f"❌ {module} - Error: {e}")
            failed_modules.append(module)
    
    if failed_modules:
        print(f"\n⚠️  Módulos con problemas: {', '.join(failed_modules)}")
        return False
    
    return True

def check_fastapi_app():
    """Verifica que la aplicación FastAPI se pueda crear"""
    print("\n🚀 Verificando aplicación FastAPI...")
    
    try:
        from main import app
        print(f"✅ Aplicación FastAPI creada: {app.title} v{app.version}")
        
        # Verificar endpoints
        routes = [route.path for route in app.routes]
        print(f"✅ {len(routes)} endpoints disponibles")
        
        return True
    except Exception as e:
        print(f"❌ Error creando aplicación FastAPI: {e}")
        return False

def main():
    """Función principal de verificación"""
    print("🔍 VERIFICACIÓN DEL SISTEMA BACKEND EVALUATE")
    print("=" * 50)
    
    checks = [
        check_python_version(),
        check_dependencies(),
        check_environment(),
        check_modules(),
        check_fastapi_app()
    ]
    
    print("\n" + "=" * 50)
    print("📊 RESUMEN DE VERIFICACIÓN")
    print("=" * 50)
    
    passed = sum(checks)
    total = len(checks)
    
    if passed == total:
        print("🎉 ¡TODOS LOS CHECKS PASARON!")
        print("✅ Tu backend está listo para funcionar")
        print("\n🚀 Para iniciar el servidor:")
        print("   python main.py")
    else:
        print(f"⚠️  {passed}/{total} checks pasaron")
        print("❌ Hay problemas que necesitan ser corregidos")
        print("\n🔧 Pasos recomendados:")
        print("1. Instala dependencias: pip install -r requirements.txt")
        print("2. Configura .env: python setup-env.py")
        print("3. Verifica credenciales de Azure")
        print("4. Ejecuta este script nuevamente")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
