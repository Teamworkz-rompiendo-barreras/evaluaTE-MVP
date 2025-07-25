#!/usr/bin/env python3
"""
Script de prueba para verificar la conexión con Azure OpenAI
"""

import os
import json
from openai import AzureOpenAI
from dotenv import load_dotenv

def main():
    print("🔍 Verificando configuración de Azure OpenAI...")
    print("=" * 50)
    
    # Cargar variables de entorno
    load_dotenv()
    
    # Obtener variables
    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")
    api_version = os.getenv("AZURE_OPENAI_API_VERSION")
    
    # Verificar variables
    print("📋 Variables de entorno:")
    print(f"  API_KEY: {'✅ Configurada' if api_key else '❌ No configurada'}")
    print(f"  ENDPOINT: {endpoint or '❌ No configurado'}")
    print(f"  DEPLOYMENT: {deployment or '❌ No configurado'}")
    print(f"  API_VERSION: {api_version or '❌ No configurado'}")
    print()
    
    if not all([api_key, endpoint, deployment, api_version]):
        print("❌ Faltan variables de entorno. Verifica tu archivo .env")
        return
    
    # Crear cliente
    try:
        client = AzureOpenAI(
            api_key=api_key,
            api_version=api_version,
            azure_endpoint=endpoint
        )
        print("✅ Cliente Azure OpenAI creado correctamente")
    except Exception as e:
        print(f"❌ Error creando cliente: {e}")
        return
    
    # Probar conexión simple
    print("\n🧪 Probando conexión básica...")
    try:
        response = client.chat.completions.create(
            model=deployment,
            messages=[{"role": "user", "content": "Hola, responde solo 'OK' si me escuchas."}],
            max_tokens=10
        )
        print(f"✅ Conexión exitosa!")
        print(f"   Respuesta: {response.choices[0].message.content}")
    except Exception as e:
        print(f"❌ Error en conexión: {e}")
        print(f"   Tipo de error: {type(e).__name__}")
        return
    
    # Probar análisis de CV (simulado)
    print("\n📄 Probando análisis de CV...")
    cv_text = """
    Juan Pérez
    Desarrollador Full Stack
    
    EXPERIENCIA:
    - Desarrollador Senior en TechCorp (2020-2023)
    - Desarrollador Junior en StartupXYZ (2018-2020)
    
    HABILIDADES:
    - JavaScript, React, Node.js
    - Python, Django
    - SQL, MongoDB
    
    EDUCACIÓN:
    - Ingeniería Informática, Universidad XYZ (2018)
    """
    
    prompt = f"""
    Analiza el siguiente CV y devuelve un JSON con:
    - strengths: puntos fuertes
    - weaknesses: áreas de mejora
    - skills: habilidades técnicas detectadas
    
    CV: {cv_text}
    """
    
    try:
        response = client.chat.completions.create(
            model=deployment,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
            temperature=0.7,
            response_format={"type": "json_object"},
        )
        
        analysis = json.loads(response.choices[0].message.content)
        print("✅ Análisis de CV exitoso!")
        print(f"   Fortalezas: {analysis.get('strengths', [])}")
        print(f"   Debilidades: {analysis.get('weaknesses', [])}")
        print(f"   Habilidades: {analysis.get('skills', [])}")
        
    except Exception as e:
        print(f"❌ Error en análisis de CV: {e}")
    
    print("\n🎉 Prueba completada!")

if __name__ == "__main__":
    main() 