#!/usr/bin/env python3
"""
Script para verificar qué deployments están disponibles en Azure OpenAI
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
API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")

print("🔍 VERIFICANDO DEPLOYMENTS DISPONIBLES")
print("=" * 60)
print(f"ENDPOINT: {ENDPOINT}")
print(f"API_VERSION: {API_VERSION}")
print()

if not all([API_KEY, ENDPOINT, API_VERSION]):
    print("❌ Faltan variables de entorno requeridas")
    sys.exit(1)

# URL para listar deployments
deployments_url = f"{ENDPOINT}/openai/deployments?api-version={API_VERSION}"

print(f"🔗 URL de consulta: {deployments_url}")
print()

try:
    # Headers requeridos
    headers = {
        "api-key": API_KEY,
        "Content-Type": "application/json"
    }
    
    print("📡 Consultando deployments disponibles...")
    response = requests.get(deployments_url, headers=headers, timeout=30)
    
    print(f"📊 Status Code: {response.status_code}")
    print(f"📊 Response Headers: {dict(response.headers)}")
    
    if response.status_code == 200:
        deployments = response.json()
        print("\n✅ DEPLOYMENTS DISPONIBLES:")
        print("-" * 40)
        
        if 'data' in deployments:
            for deployment in deployments['data']:
                print(f"📋 Nombre: {deployment.get('id', 'N/A')}")
                print(f"   Modelo: {deployment.get('model', 'N/A')}")
                print(f"   Estado: {deployment.get('status', 'N/A')}")
                print(f"   Creado: {deployment.get('created_at', 'N/A')}")
                print()
        else:
            print("❌ No se encontraron deployments en la respuesta")
            print(f"Respuesta completa: {deployments}")
    
    elif response.status_code == 401:
        print("❌ Error 401: Problema de autenticación")
        print("   Verifica que la API_KEY sea correcta")
    elif response.status_code == 403:
        print("❌ Error 403: Sin permisos para acceder al recurso")
        print("   Verifica que tengas permisos para listar deployments")
    elif response.status_code == 404:
        print("❌ Error 404: Recurso no encontrado")
        print("   Verifica que el ENDPOINT sea correcto")
    else:
        print(f"❌ Error {response.status_code}: {response.text}")
    
    # También probar con la API de modelos
    print("\n🔍 VERIFICANDO MODELOS DISPONIBLES...")
    models_url = f"{ENDPOINT}/openai/models?api-version={API_VERSION}"
    print(f"🔗 URL de modelos: {models_url}")
    
    response_models = requests.get(models_url, headers=headers, timeout=30)
    print(f"📊 Status Code (modelos): {response_models.status_code}")
    
    if response_models.status_code == 200:
        models = response_models.json()
        print("\n✅ MODELOS DISPONIBLES:")
        print("-" * 30)
        
        if 'data' in models:
            for model in models['data']:
                print(f"🤖 ID: {model.get('id', 'N/A')}")
                print(f"   Tipo: {model.get('object', 'N/A')}")
                print(f"   Propietario: {model.get('owned_by', 'N/A')}")
                print()
        else:
            print("❌ No se encontraron modelos en la respuesta")
    
except requests.exceptions.RequestException as e:
    print(f"❌ Error de conexión: {e}")
except Exception as e:
    print(f"❌ Error general: {e}")

print("\n" + "=" * 60)
print("🏁 Fin de la verificación")
