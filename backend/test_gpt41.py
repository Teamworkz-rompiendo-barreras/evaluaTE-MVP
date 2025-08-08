#!/usr/bin/env python3
"""
Script de prueba específico para GPT-4.1
"""

import os
from dotenv import load_dotenv
from openai import AzureOpenAI

# Cargar variables de entorno
load_dotenv()

# Variables de entorno
API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
DEPLOYMENT = "gpt-4.1"
API_VERSION = "2024-02-15-preview"  # Versión estándar que funciona

print("🔍 PRUEBA ESPECÍFICA GPT-4.1")
print("=" * 50)
print(f"API_KEY: {'✅ Configurada' if API_KEY else '❌ No configurada'}")
print(f"ENDPOINT: {ENDPOINT}")
print(f"DEPLOYMENT: {DEPLOYMENT}")
print(f"API_VERSION: {API_VERSION}")
print()

if not all([API_KEY, ENDPOINT]):
    print("❌ Faltan variables de entorno requeridas")
    exit(1)

try:
    print("🔧 Configurando cliente Azure OpenAI...")
    client = AzureOpenAI(
        api_key=API_KEY,
        api_version=API_VERSION,
        azure_endpoint=ENDPOINT
    )
    print("✅ Cliente configurado correctamente")
    
    print(f"\n📝 Probando deployment: '{DEPLOYMENT}'")
    print(f"🔗 URL: {ENDPOINT}/openai/deployments/{DEPLOYMENT}/chat/completions?api-version={API_VERSION}")
    
    response = client.chat.completions.create(
        model=DEPLOYMENT,
        messages=[{"role": "user", "content": "Hola, responde con 'OK' si me escuchas."}],
        temperature=0.1,
        max_tokens=10,
        timeout=30
    )
    
    print(f"✅ ÉXITO con deployment: '{DEPLOYMENT}'")
    print(f"   Respuesta: {response.choices[0].message.content}")
    
    # Probar con un nombre que contenga caracteres especiales
    print(f"\n🧪 Probando con nombre que contiene caracteres especiales...")
    test_prompt = f"""
    Genera un informe profesional para el candidato: "María (Ana) García-López"
    
    Responde solo con: "Nombre procesado correctamente"
    """
    
    response2 = client.chat.completions.create(
        model=DEPLOYMENT,
        messages=[{"role": "user", "content": test_prompt}],
        temperature=0.1,
        max_tokens=50,
        timeout=30
    )
    
    print(f"✅ Prueba con caracteres especiales: {response2.choices[0].message.content}")
    
except Exception as e:
    print(f"❌ Error: {str(e)}")
    if "404" in str(e):
        print("   → Error 404: Deployment no encontrado")
        print("   → Verifica que el deployment 'gpt-4.1' esté creado en Azure OpenAI")
    elif "401" in str(e):
        print("   → Error 401: Problema de autenticación")
    elif "403" in str(e):
        print("   → Error 403: Sin permisos")

print("\n" + "=" * 50)
print("🏁 Fin de la prueba")
