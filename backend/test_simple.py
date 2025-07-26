# backend/test_simple.py

import pytest
from fastapi.testclient import TestClient
from main import app

# Crear el cliente de test
client = TestClient(app)

def test_home_endpoint():
    """Test básico del endpoint raíz"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "Bienvenida/o a EvaluaTE MVP" in data["message"]

def test_api_docs():
    """Test de que la documentación de la API está disponible"""
    response = client.get("/docs")
    assert response.status_code == 200

def test_openapi_schema():
    """Test del esquema OpenAPI"""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    data = response.json()
    assert "openapi" in data
    assert "paths" in data

if __name__ == "__main__":
    # Ejecutar tests básicos
    print("Ejecutando tests básicos...")
    
    # Test del endpoint raíz
    try:
        response = client.get("/")
        print(f"✅ Endpoint raíz: {response.status_code}")
        if response.status_code == 200:
            print(f"   Mensaje: {response.json()}")
    except Exception as e:
        print(f"❌ Error en endpoint raíz: {e}")
    
    # Test de la documentación
    try:
        response = client.get("/docs")
        print(f"✅ Documentación API: {response.status_code}")
    except Exception as e:
        print(f"❌ Error en documentación: {e}")
    
    print("Tests básicos completados.") 