#!/usr/bin/env python3
"""
Diagnóstico profundo del recurso de Azure OpenAI
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

print("🔍 DIAGNÓSTICO PROFUNDO DE AZURE OPENAI")
print("=" * 70)
print(f"ENDPOINT: {ENDPOINT}")
print(f"API_KEY: {'✅ Configurada' if API_KEY else '❌ No configurada'}")
print()

if not all([API_KEY, ENDPOINT]):
    print("❌ Faltan variables de entorno requeridas")
    sys.exit(1)

# 1. Verificar conectividad básica
print("1️⃣ VERIFICANDO CONECTIVIDAD BÁSICA...")
try:
    # Intentar conectar sin autenticación
    response = requests.get(ENDPOINT, timeout=10)
    print(f"   Status: {response.status_code}")
    if response.status_code == 401:
        print("   ✅ Endpoint responde (autenticación requerida)")
    elif response.status_code == 404:
        print("   ❌ Endpoint no encontrado")
    else:
        print(f"   ⚠️  Respuesta inesperada: {response.status_code}")
except Exception as e:
    print(f"   ❌ Error de conectividad: {e}")

print()

# 2. Verificar diferentes rutas de la API
print("2️⃣ VERIFICANDO DIFERENTES RUTAS DE LA API...")

# Probar diferentes rutas con una versión de API estándar
test_routes = [
    "/openai/deployments",
    "/openai/models", 
    "/openai/chat/completions",
    "/openai/completions",
    "/openai/embeddings"
]

api_version = "2024-02-15-preview"

for route in test_routes:
    url = f"{ENDPOINT}{route}?api-version={api_version}"
    print(f"   📡 Probando: {route}")
    
    try:
        headers = {
            "api-key": API_KEY,
            "Content-Type": "application/json"
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        print(f"      Status: {response.status_code}")
        
        if response.status_code == 200:
            print(f"      ✅ Ruta válida!")
        elif response.status_code == 404:
            print(f"      ❌ Ruta no encontrada")
        elif response.status_code == 401:
            print(f"      ⚠️  Autenticación requerida")
        elif response.status_code == 403:
            print(f"      ❌ Sin permisos")
        else:
            print(f"      ⚠️  Respuesta: {response.text[:100]}...")
            
    except Exception as e:
        print(f"      ❌ Error: {e}")
    
    print()

# 3. Verificar si el problema es de autenticación
print("3️⃣ VERIFICANDO AUTENTICACIÓN...")

# Probar con diferentes formatos de headers
test_headers = [
    {"api-key": API_KEY},
    {"api-key": API_KEY, "Content-Type": "application/json"},
    {"Authorization": f"Bearer {API_KEY}"},
    {"x-api-key": API_KEY}
]

for i, headers in enumerate(test_headers, 1):
    url = f"{ENDPOINT}/openai/deployments?api-version={api_version}"
    print(f"   🔑 Probando headers {i}: {list(headers.keys())}")
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        print(f"      Status: {response.status_code}")
        
        if response.status_code == 200:
            print(f"      ✅ Autenticación exitosa!")
            break
        elif response.status_code == 401:
            print(f"      ❌ Autenticación fallida")
        elif response.status_code == 404:
            print(f"      ❌ Recurso no encontrado")
        else:
            print(f"      ⚠️  Respuesta: {response.text[:100]}...")
            
    except Exception as e:
        print(f"      ❌ Error: {e}")
    
    print()

# 4. Verificar si el endpoint tiene el formato correcto
print("4️⃣ VERIFICANDO FORMATO DEL ENDPOINT...")
from urllib.parse import urlparse

parsed = urlparse(ENDPOINT)
print(f"   Esquema: {parsed.scheme}")
print(f"   Dominio: {parsed.netloc}")
print(f"   Ruta: {parsed.path}")

if not parsed.netloc.endswith('.openai.azure.com'):
    print("   ⚠️  El dominio no termina en .openai.azure.com")
else:
    print("   ✅ Formato de dominio correcto")

if parsed.path != '':
    print("   ⚠️  El endpoint no debería tener ruta adicional")
else:
    print("   ✅ Endpoint sin ruta adicional")

print()

# 5. Verificar si hay problemas de red/proxy
print("5️⃣ VERIFICANDO CONFIGURACIÓN DE RED...")

# Verificar variables de entorno de proxy
proxy_vars = ['HTTP_PROXY', 'HTTPS_PROXY', 'ALL_PROXY', 'NO_PROXY']
for var in proxy_vars:
    value = os.getenv(var)
    if value:
        print(f"   ⚠️  {var} está configurado: {value}")
    else:
        print(f"   ✅ {var} no está configurado")

print()

print("=" * 70)
print("🏁 Fin del diagnóstico profundo")
print()
print("💡 RECOMENDACIONES:")
print("1. Verifica que el recurso de Azure OpenAI esté activo en el portal")
print("2. Verifica que tengas permisos para acceder al recurso")
print("3. Verifica que el endpoint sea correcto")
print("4. Verifica que la API key sea válida")
print("5. Considera crear un nuevo deployment en el portal de Azure")
