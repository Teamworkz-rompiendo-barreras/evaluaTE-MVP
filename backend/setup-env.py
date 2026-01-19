#!/usr/bin/env python3
"""
Script para configurar automáticamente el archivo .env del backend
"""

import os
import shutil
from pathlib import Path

def setup_environment():
    """Configura el archivo .env del backend"""
    
    print("🔧 CONFIGURACIÓN AUTOMÁTICA DEL ENTORNO BACKEND")
    print("=" * 50)
    
    # Verificar si ya existe .env
    env_file = Path(".env")
    env_example = Path("env.example")
    
    if env_file.exists():
        print("⚠️  El archivo .env ya existe")
        response = input("¿Quieres sobrescribirlo? (s/N): ").lower()
        if response != 's':
            print("❌ Configuración cancelada")
            return False
    
    # Copiar env.example a .env
    if env_example.exists():
        try:
            shutil.copy2(env_example, env_file)
            print("✅ Archivo .env creado desde env.example")
        except Exception as e:
            print(f"❌ Error copiando archivo: {e}")
            return False
    else:
        print("❌ No se encontró env.example")
        return False
    
    # Mostrar instrucciones
    print("\n📋 PRÓXIMOS PASOS:")
    print("1. Edita el archivo .env con tu API Key de Google Gemini")
    print("2. La variable más importante es:")
    print("   - GEMINI_API_KEY")
    print("3. Reinicia el backend después de configurar")
    
    print("\n🔗 Para obtener tu API Key:")
    print("   - Ve a https://aistudio.google.com/")
    print("   - Crea una API Key gratuita")
    print("   - Cópiala en el archivo .env")
    
    print("\n✅ Configuración completada!")
    print("📁 Archivo .env creado en:", env_file.absolute())
    
    return True

if __name__ == "__main__":
    setup_environment()
