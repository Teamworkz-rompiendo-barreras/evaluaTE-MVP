#!/usr/bin/env python3
"""
Script de prueba para diagnosticar problemas de conexión con Azure OpenAI
"""

import os
import sys
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Variables de entorno
API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT")
API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")

print("🔍 DIAGNÓSTICO DE AZURE OPENAI")
print("=" * 50)
print(f"API_KEY: {'✅ Configurada' if API_KEY else '❌ No configurada'}")
print(f"ENDPOINT: {ENDPOINT}")
print(f"DEPLOYMENT: {DEPLOYMENT}")
print(f"API_VERSION: {API_VERSION}")
print()

if not all([API_KEY, ENDPOINT, DEPLOYMENT, API_VERSION]):
    print("❌ Faltan variables de entorno requeridas")
    sys.exit(1)

try:
    from openai import AzureOpenAI
    
    print("🔧 Configurando cliente Azure OpenAI...")
    client = AzureOpenAI(
        api_key=API_KEY,
        api_version=API_VERSION,
        azure_endpoint=ENDPOINT
    )
    print("✅ Cliente configurado correctamente")
    
    # Probar diferentes variaciones del nombre del deployment
    deployment_variations = [
        DEPLOYMENT.strip(),
        f"{DEPLOYMENT.strip()} (version:{API_VERSION})",
        DEPLOYMENT.strip().replace(" ", ""),
        "gpt-4o",
        "gpt-4o-mini",
        "gpt-35-turbo"
    ]
    
    print("\n🧪 Probando diferentes nombres de deployment...")
    
    for deployment_name in deployment_variations:
        print(f"\n📝 Probando deployment: '{deployment_name}'")
        try:
            response = client.chat.completions.create(
                model=deployment_name,
                messages=[{"role": "user", "content": "Hola, responde con 'OK' si me escuchas."}],
                temperature=0.1,
                max_tokens=10,
                timeout=30
            )
            print(f"✅ ÉXITO con deployment: '{deployment_name}'")
            print(f"   Respuesta: {response.choices[0].message.content}")
            break
        except Exception as e:
            print(f"❌ Error con deployment '{deployment_name}': {str(e)}")
            if "404" in str(e):
                print("   → Error 404: Deployment no encontrado")
            elif "401" in str(e):
                print("   → Error 401: Problema de autenticación")
            elif "403" in str(e):
                print("   → Error 403: Sin permisos")
    
    print("\n🔍 Información adicional:")
    print(f"URL completa que se está usando: {ENDPOINT}/openai/deployments/{DEPLOYMENT.strip()}/chat/completions?api-version={API_VERSION}")
    
except ImportError:
    print("❌ Error: No se pudo importar la biblioteca 'openai'")
    print("   Instala con: pip install openai")
except Exception as e:
    print(f"❌ Error general: {e}")

print("\n" + "=" * 50)
print("🏁 Fin del diagnóstico")
