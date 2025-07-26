#!/usr/bin/env python3
"""
Script de prueba para analizar el CV real usando la API del backend
"""

import requests
import json
import os

def test_cv_analysis():
    print("🔍 Probando análisis de CV real...")
    print("=" * 50)
    
    # Verificar que el archivo existe
    cv_path = "cv_prueba.pdf"
    if not os.path.exists(cv_path):
        print(f"❌ Error: No se encuentra el archivo {cv_path}")
        return
    
    print(f"✅ Archivo encontrado: {cv_path}")
    print(f"📊 Tamaño: {os.path.getsize(cv_path)} bytes")
    
    # URL del endpoint
    url = "http://localhost:8000/api/analyze-cv"
    
    try:
        # Preparar el archivo para envío
        with open(cv_path, 'rb') as f:
            files = {'cv': (cv_path, f, 'application/pdf')}
            
            print("📤 Enviando archivo al backend...")
            response = requests.post(url, files=files)
        
        print(f"📥 Respuesta del servidor: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Análisis exitoso!")
            print("\n📋 Resultado del análisis:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            
            # Mostrar resumen
            print("\n📊 Resumen del análisis:")
            print(f"  Estructura: {result.get('structure', 'N/A')}")
            print(f"  Coherencia: {result.get('coherence', 'N/A')}")
            print(f"  Experiencia: {result.get('experience', 'N/A')}")
            print(f"  Habilidades detectadas: {len(result.get('skills', []))}")
            print(f"  Educación detectada: {len(result.get('education', []))}")
            
            if result.get('alerts'):
                print(f"  Alertas: {', '.join(result['alerts'])}")
            
        else:
            print(f"❌ Error en el análisis: {response.status_code}")
            print(f"Respuesta: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Error: No se puede conectar al backend. Asegúrate de que esté ejecutándose en puerto 8000.")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

if __name__ == "__main__":
    test_cv_analysis() 