#!/usr/bin/env python3
"""
Script de prueba para verificar el formato de respuesta de Azure Document Intelligence
"""

import os
import sys
import logging
from dotenv import load_dotenv

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cargar variables de entorno
load_dotenv()

def test_document_intelligence_config():
    """Prueba la configuración de Document Intelligence"""
    print("🔧 Probando configuración de Document Intelligence...")
    
    # Verificar variables de entorno
    endpoint = os.getenv('AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT')
    key = os.getenv('AZURE_DOCUMENT_INTELLIGENCE_KEY')
    
    print(f"Endpoint: {'✅' if endpoint else '❌'}")
    print(f"Key: {'✅' if key else '❌'}")
    
    if not endpoint or not key:
        print("❌ Document Intelligence no está configurado")
        return False
    
    # Verificar que el endpoint tiene el formato correcto
    if not endpoint.endswith('.cognitiveservices.azure.com/'):
        print("⚠️ Endpoint no tiene el formato esperado")
    
    print("✅ Configuración básica correcta")
    return True

def test_document_intelligence_import():
    """Prueba la importación de las librerías"""
    print("📦 Probando importación de librerías...")
    
    try:
        from azure.ai.formrecognizer import DocumentAnalysisClient
        from azure.core.credentials import AzureKeyCredential
        print("✅ Librerías importadas correctamente")
        return True
    except ImportError as e:
        print(f"❌ Error importando librerías: {e}")
        return False

def test_document_intelligence_client():
    """Prueba la creación del cliente"""
    print("🔌 Probando creación del cliente...")
    
    try:
        from azure.ai.formrecognizer import DocumentAnalysisClient
        from azure.core.credentials import AzureKeyCredential
        
        endpoint = os.getenv('AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT')
        key = os.getenv('AZURE_DOCUMENT_INTELLIGENCE_KEY')
        
        client = DocumentAnalysisClient(
            endpoint=endpoint, 
            credential=AzureKeyCredential(key)
        )
        print("✅ Cliente creado correctamente")
        return client
    except Exception as e:
        print(f"❌ Error creando cliente: {e}")
        return None

def test_document_intelligence_model():
    """Prueba que el modelo esté disponible"""
    print("🤖 Probando modelo prebuilt-layout...")
    
    client = test_document_intelligence_client()
    if not client:
        return False
    
    try:
        # Crear un PDF de prueba simple
        import tempfile
        from reportlab.pdfgen import canvas
        
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
            # Crear un PDF simple con texto
            c = canvas.Canvas(temp_file.name)
            c.drawString(100, 750, "Test Document Intelligence")
            c.drawString(100, 700, "Este es un documento de prueba")
            c.save()
            
            # Probar el análisis
            with open(temp_file.name, "rb") as document:
                print("📄 Enviando documento de prueba...")
                poller = client.begin_analyze_document("prebuilt-layout", document)
                result = poller.result()
                
                print(f"✅ Análisis completado")
                print(f"📝 Contenido extraído: {len(result.content)} caracteres")
                print(f"📄 Primeros 200 caracteres: {result.content[:200]}")
                
                # Verificar estructura del resultado
                print("🔍 Verificando estructura del resultado...")
                print(f"Tiene content: {'✅' if hasattr(result, 'content') else '❌'}")
                print(f"Tiene pages: {'✅' if hasattr(result, 'pages') else '❌'}")
                print(f"Tiene tables: {'✅' if hasattr(result, 'tables') else '❌'}")
                
                if hasattr(result, 'pages'):
                    print(f"Número de páginas: {len(result.pages)}")
                
                return True
                
    except Exception as e:
        print(f"❌ Error probando modelo: {e}")
        return False
    finally:
        # Limpiar archivo temporal
        if 'temp_file' in locals():
            os.unlink(temp_file.name)

def main():
    """Función principal de pruebas"""
    print("🚀 Iniciando pruebas de Document Intelligence...")
    print("=" * 50)
    
    # Prueba 1: Configuración
    if not test_document_intelligence_config():
        print("❌ Pruebas fallidas en configuración")
        return
    
    # Prueba 2: Importación
    if not test_document_intelligence_import():
        print("❌ Pruebas fallidas en importación")
        return
    
    # Prueba 3: Cliente
    if not test_document_intelligence_client():
        print("❌ Pruebas fallidas en creación de cliente")
        return
    
    # Prueba 4: Modelo
    if not test_document_intelligence_model():
        print("❌ Pruebas fallidas en modelo")
        return
    
    print("=" * 50)
    print("✅ Todas las pruebas completadas exitosamente")

if __name__ == "__main__":
    main()
