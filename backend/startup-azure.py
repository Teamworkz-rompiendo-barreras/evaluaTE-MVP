#!/usr/bin/env python3
"""
Script de inicio simplificado para Azure Web App
"""

import os
import sys
import subprocess

def main():
    print("🚀 Iniciando EvaluaTE Backend en Azure...")
    
    # Obtener puerto de Azure (por defecto 8080)
    port = os.getenv('PORT', '8080')
    print(f"🌐 Puerto: {port}")
    
    # Iniciar uvicorn directamente
    subprocess.run([
        sys.executable, "-m", "uvicorn", 
        "main:app", 
        "--host", "0.0.0.0", 
        "--port", port
    ])

if __name__ == "__main__":
    main() 