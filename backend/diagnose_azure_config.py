#!/usr/bin/env python3
"""
Script de diagnóstico para verificar la configuración de Azure en producción
"""

import os
import sys
import logging

# Cargar variables de entorno desde .env
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ Archivo .env cargado")
except ImportError:
    print("⚠️ python-dotenv no está instalado")
except Exception as e:
    print(f"⚠️ Error cargando .env: {e}")

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_environment_variables():
    """Verificar variables de entorno críticas"""
    print("🔍 Verificando variables de entorno...")
    
    # Variables de Azure OpenAI
    azure_openai_vars = [
        'AZURE_OPENAI_API_KEY',
        'AZURE_OPENAI_ENDPOINT', 
        'AZURE_OPENAI_DEPLOYMENT',
        'AZURE_OPENAI_API_VERSION'
    ]
    
    # Variables de Azure Document Intelligence
    azure_doc_vars = [
        'AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT',
        'AZURE_DOCUMENT_INTELLIGENCE_KEY'
    ]
    
    print("\n📋 Variables de Azure OpenAI:")
    for var in azure_openai_vars:
        value = os.getenv(var)
        status = "✅" if value else "❌"
        print(f"  {status} {var}: {'CONFIGURADA' if value else 'NO CONFIGURADA'}")
    
    print("\n📋 Variables de Azure Document Intelligence:")
    for var in azure_doc_vars:
        value = os.getenv(var)
        status = "✅" if value else "❌"
        print(f"  {status} {var}: {'CONFIGURADA' if value else 'NO CONFIGURADA'}")
    
    # Verificar si estamos en Azure
    is_azure = any([
        os.getenv('WEBSITE_SITE_NAME'),
        os.getenv('WEBSITE_INSTANCE_ID'),
        os.getenv('AZURE_WEBAPP_NAME')
    ])
    
    print(f"\n🌐 Entorno: {'Azure App Service' if is_azure else 'Local/Desarrollo'}")
    
    return {
        'azure_openai_configured': all(os.getenv(var) for var in azure_openai_vars),
        'azure_doc_configured': all(os.getenv(var) for var in azure_doc_vars),
        'is_azure': is_azure
    }

def test_azure_openai():
    """Probar conexión a Azure OpenAI"""
    print("\n🤖 Probando Azure OpenAI...")
    
    try:
        from openai import AzureOpenAI
        
        api_key = os.getenv('AZURE_OPENAI_API_KEY')
        endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')
        deployment = os.getenv('AZURE_OPENAI_DEPLOYMENT')
        api_version = os.getenv('AZURE_OPENAI_API_VERSION')
        
        if not all([api_key, endpoint, deployment, api_version]):
            print("❌ Azure OpenAI no configurado completamente")
            return False
        
        client = AzureOpenAI(
            api_key=api_key,
            api_version=api_version,
            azure_endpoint=endpoint
        )
        
        # Prueba simple
        response = client.chat.completions.create(
            model=deployment,
            messages=[{"role": "user", "content": "Hola, esto es una prueba"}],
            max_tokens=10
        )
        
        print("✅ Azure OpenAI funcionando correctamente")
        return True
        
    except Exception as e:
        print(f"❌ Error con Azure OpenAI: {e}")
        return False

def test_azure_document_intelligence():
    """Probar conexión a Azure Document Intelligence"""
    print("\n📄 Probando Azure Document Intelligence...")
    
    try:
        from azure.ai.formrecognizer import DocumentAnalysisClient
        from azure.core.credentials import AzureKeyCredential
        
        endpoint = os.getenv('AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT')
        key = os.getenv('AZURE_DOCUMENT_INTELLIGENCE_KEY')
        
        if not endpoint or not key:
            print("❌ Azure Document Intelligence no configurado")
            return False
        
        client = DocumentAnalysisClient(
            endpoint=endpoint, 
            credential=AzureKeyCredential(key)
        )
        
        print("✅ Cliente de Document Intelligence creado correctamente")
        return True
        
    except Exception as e:
        print(f"❌ Error con Azure Document Intelligence: {e}")
        return False

def main():
    print("🚀 Diagnóstico de configuración de Azure")
    print("=" * 50)
    
    # Verificar variables de entorno
    config_status = check_environment_variables()
    
    # Probar conexiones
    openai_working = test_azure_openai()
    doc_intelligence_working = test_azure_document_intelligence()
    
    # Resumen
    print("\n" + "=" * 50)
    print("📊 RESUMEN DEL DIAGNÓSTICO")
    print("=" * 50)
    
    print(f"Azure OpenAI: {'✅ FUNCIONANDO' if openai_working else '❌ PROBLEMA'}")
    print(f"Document Intelligence: {'✅ FUNCIONANDO' if doc_intelligence_working else '❌ PROBLEMA'}")
    print(f"Entorno: {'🌐 Azure App Service' if config_status['is_azure'] else '💻 Local/Desarrollo'}")
    
    if not config_status['azure_doc_configured']:
        print("\n⚠️  RECOMENDACIONES:")
        print("1. Configura las variables de entorno en Azure App Service:")
        print("   - AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT")
        print("   - AZURE_DOCUMENT_INTELLIGENCE_KEY")
        print("2. O usa el fallback automático (PyMuPDF) que ya está implementado")
    
    if config_status['is_azure'] and not config_status['azure_doc_configured']:
        print("\n🔧 Para configurar en Azure App Service:")
        print("1. Ve al portal de Azure")
        print("2. Navega a tu App Service")
        print("3. Configuración > Configuración de la aplicación")
        print("4. Agrega las variables de entorno necesarias")

if __name__ == "__main__":
    main()
