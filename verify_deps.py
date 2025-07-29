#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para verificar dependencias de manera robusta
"""

import sys
import subprocess
import importlib
import os

def check_import(module_name):
    """Verifica si un módulo se puede importar"""
    try:
        importlib.import_module(module_name)
        return True
    except ImportError:
        return False

def check_import_with_fallback(module_name, fallback_names=None):
    """Verifica importación con nombres alternativos"""
    if check_import(module_name):
        return True
    
    if fallback_names:
        for fallback in fallback_names:
            if check_import(fallback):
                return True
    
    return False

def main():
    print("🔍 Verificando dependencias de manera robusta...")
    
    # Lista de dependencias críticas con sus nombres de importación
    critical_deps = {
        "python-dotenv": ["dotenv"],
        "openai": ["openai"],
        "pytesseract": ["pytesseract"],
        "Pillow": ["PIL"],
        "PyMuPDF": ["fitz"],
        "fastapi": ["fastapi"],
        "uvicorn": ["uvicorn"],
        "pypdf": ["pypdf"],
        "reportlab": ["reportlab"]
    }
    
    missing_deps = []
    working_deps = []
    
    for package_name, import_names in critical_deps.items():
        if check_import_with_fallback(import_names[0], import_names[1:] if len(import_names) > 1 else None):
            print(f"✅ {package_name}")
            working_deps.append(package_name)
        else:
            print(f"❌ {package_name}")
            missing_deps.append(package_name)
    
    print(f"\n📊 Resumen:")
    print(f"   ✅ Funcionando: {len(working_deps)}/{len(critical_deps)}")
    print(f"   ❌ Faltantes: {len(missing_deps)}")
    
    if missing_deps:
        print(f"\n⚠️  Dependencias faltantes: {', '.join(missing_deps)}")
        print("💡 Ejecuta: pip install " + " ".join(missing_deps))
        return False
    else:
        print("\n🎉 ¡Todas las dependencias están funcionando correctamente!")
        return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 