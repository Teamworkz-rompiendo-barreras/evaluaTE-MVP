#!/usr/bin/env python3
"""
Script para verificar qué modelos están disponibles en Azure OpenAI
"""

import os
import sys
import requests
import json
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Variables de entorno
API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")

print("🔍 VERIFICANDO MODELOS DISPONIBLES")
print("=" * 60)
print(f"ENDPOINT: {ENDPOINT}")
print()

if not all([API_KEY, ENDPOINT]):
    print("❌ Faltan variables de entorno requeridas")
    sys.exit(1)

# Probar diferentes versiones de API para la ruta de modelos
api_versions = [
    "2024-02-15-preview",
    "2024-02-01",
    "2023-12-01-preview",
    "2023-09-01-preview",
    "2023-08-01-preview",
    "2023-07-01-preview",
    "2023-06-01",
    "2023-05-15"
]

print("🧪 Probando diferentes versiones de API para modelos...")
print()

for api_version in api_versions:
    print(f"📝 Probando API version: {api_version}")
    
    url = f"{ENDPOINT}/openai/models?api-version={api_version}"
    
    try:
        headers = {
            "api-key": API_KEY,
            "Content-Type": "application/json"
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            print(f"✅ ÉXITO con API version: {api_version}")
            models = response.json()
            
            if 'data' in models and models['data']:
                print(f"   📋 Modelos disponibles: {len(models['data'])}")
                print("   🤖 Lista de modelos:")
                
                for model in models['data']:
                    model_id = model.get('id', 'N/A')
                    model_object = model.get('object', 'N/A')
                    model_owned_by = model.get('owned_by', 'N/A')
                    
                    print(f"      - {model_id}")
                    print(f"        Tipo: {model_object}")
                    print(f"        Propietario: {model_owned_by}")
                    print()
                
                print(f"   💡 RECOMENDACIÓN: Usar esta versión para crear deployments")
                print(f"   🔧 API_VERSION recomendada: {api_version}")
                
                # Mostrar instrucciones para crear deployment
                print("\n" + "=" * 60)
                print("📋 INSTRUCCIONES PARA CREAR DEPLOYMENT:")
                print("=" * 60)
                print("1. Ve al Portal de Azure: https://portal.azure.com")
                print("2. Busca tu recurso 'teamworkzevaluate-openai'")
                print("3. Ve a 'Model deployments' en el menú lateral")
                print("4. Haz clic en 'Create' o 'Crear'")
                print("5. Selecciona uno de los modelos disponibles arriba")
                print("6. Dale un nombre al deployment (ej: 'gpt-4o')")
                print("7. Configura los parámetros según necesites")
                print("8. Haz clic en 'Create'")
                print()
                print("🔧 DESPUÉS DE CREAR EL DEPLOYMENT:")
                print(f"   - Actualiza AZURE_OPENAI_API_VERSION={api_version}")
                print("   - Usa el nombre del deployment en AZURE_OPENAI_DEPLOYMENT")
                print("   - Reinicia la aplicación")
                
                break
            else:
                print("   ⚠️  No hay modelos disponibles")
        else:
            print(f"   ❌ Error {response.status_code}: {response.text[:100]}...")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print()

print("\n" + "=" * 60)
print("🏁 Fin de la verificación")
