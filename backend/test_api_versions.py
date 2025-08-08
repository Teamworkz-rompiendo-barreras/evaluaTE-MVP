#!/usr/bin/env python3
"""
Script para probar diferentes versiones de la API de Azure OpenAI
"""

import os
import sys
import requests
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Variables de entorno
API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")

print("🔍 PROBANDO DIFERENTES VERSIONES DE API")
print("=" * 60)
print(f"ENDPOINT: {ENDPOINT}")
print()

if not all([API_KEY, ENDPOINT]):
    print("❌ Faltan variables de entorno requeridas")
    sys.exit(1)

# Versiones de API a probar (ordenadas por popularidad)
api_versions = [
    "2024-02-15-preview",
    "2024-02-01",
    "2023-12-01-preview", 
    "2023-09-01-preview",
    "2023-08-01-preview",
    "2023-07-01-preview",
    "2023-06-01",
    "2023-05-15",
    "2024-11-20"  # La versión actual que no funciona
]

print("🧪 Probando versiones de API...")
print()

for api_version in api_versions:
    print(f"📝 Probando API version: {api_version}")
    
    # URL para listar deployments
    deployments_url = f"{ENDPOINT}/openai/deployments?api-version={api_version}"
    
    try:
        # Headers requeridos
        headers = {
            "api-key": API_KEY,
            "Content-Type": "application/json"
        }
        
        response = requests.get(deployments_url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            print(f"✅ ÉXITO con API version: {api_version}")
            deployments = response.json()
            
            if 'data' in deployments and deployments['data']:
                print(f"   📋 Deployments encontrados: {len(deployments['data'])}")
                for deployment in deployments['data']:
                    print(f"      - {deployment.get('id', 'N/A')} ({deployment.get('model', 'N/A')})")
            else:
                print("   ⚠️  No hay deployments configurados")
            
            print(f"   💡 RECOMENDACIÓN: Usar esta versión en .env")
            print(f"   🔧 Cambiar AZURE_OPENAI_API_VERSION={api_version}")
            break
            
        elif response.status_code == 404:
            print(f"❌ Error 404: Versión no soportada")
        elif response.status_code == 401:
            print(f"❌ Error 401: Problema de autenticación")
        elif response.status_code == 403:
            print(f"❌ Error 403: Sin permisos")
        else:
            print(f"❌ Error {response.status_code}: {response.text[:100]}...")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión: {e}")
    except Exception as e:
        print(f"❌ Error general: {e}")
    
    print()

print("=" * 60)
print("🏁 Fin de las pruebas")
