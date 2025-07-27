#!/usr/bin/env python3
"""
Script de inicio para la aplicación EvaluaTE MVP
Verifica que el entorno virtual esté activado y ejecuta la aplicación
"""

import sys
import os
import subprocess
from pathlib import Path

def check_venv():
    """Verifica si el entorno virtual está activado"""
    return hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)

def activate_venv():
    """Intenta activar el entorno virtual"""
    venv_path = Path(__file__).parent / "venv"
    if not venv_path.exists():
        print("❌ Error: No se encontró el entorno virtual en ./venv")
        print("Ejecuta: python -m venv venv")
        return False
    
    # En Windows/Linux, el script de activación está en diferentes ubicaciones
    if os.name == 'nt':  # Windows
        activate_script = venv_path / "Scripts" / "activate.bat"
    else:  # Linux/Mac
        activate_script = venv_path / "bin" / "activate"
    
    if not activate_script.exists():
        print(f"❌ Error: No se encontró el script de activación en {activate_script}")
        return False
    
    print("✅ Entorno virtual detectado")
    return True

def check_dependencies():
    """Verifica que todas las dependencias estén instaladas"""
    required_packages = [
        'fastapi',
        'uvicorn',
        'openai',
        'pypdf',
        'pydantic',
        'dotenv'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
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
    print("🚀 Iniciando EvaluaTE MVP Backend...")
    print("=" * 50)
    
    # Verificar entorno virtual
    if not check_venv():
        print("\n💡 Para activar el entorno virtual manualmente:")
        print("   source venv/bin/activate  # Linux/Mac")
        print("   venv\\Scripts\\activate     # Windows")
        return 1
    
    # Verificar dependencias
    print("\n📦 Verificando dependencias...")
    if not check_dependencies():
        return 1
    
    print("\n✅ Todo listo para ejecutar la aplicación")
    print("\n💡 Para ejecutar la aplicación:")
    print("   uvicorn main:app --reload --host 0.0.0.0 --port 8000")
    print("\n💡 O ejecuta directamente:")
    print("   python main.py")
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 