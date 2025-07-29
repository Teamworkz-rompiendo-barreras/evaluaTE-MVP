#!/usr/bin/env python3
"""
Script de configuración para Azure OpenAI
Este script ayuda a configurar Azure OpenAI correctamente para la aplicación EvaluaTE.
"""

import os
import sys
from dotenv import load_dotenv
from openai import AzureOpenAI

def check_env_file():
    """Verifica si existe el archivo .env"""
    if not os.path.exists('.env'):
        print("❌ No se encontró el archivo .env")
        print("💡 Copia env.example a .env y configura las variables:")
        print("   cp env.example .env")
        return False
    return True

def load_config():
    """Carga la configuración desde .env"""
    load_dotenv()
    
    config = {
        'api_key': os.getenv('AZURE_OPENAI_API_KEY'),
        'endpoint': os.getenv('AZURE_OPENAI_ENDPOINT'),
        'deployment': os.getenv('AZURE_OPENAI_DEPLOYMENT'),
        'api_version': os.getenv('AZURE_OPENAI_API_VERSION')
    }
    
    return config

def validate_config(config):
    """Valida la configuración"""
    missing = []
    
    if not config['api_key'] or config['api_key'] == 'tu_api_key_aqui':
        missing.append('AZURE_OPENAI_API_KEY')
    
    if not config['endpoint'] or config['endpoint'] == 'https://tu-recurso.openai.azure.com':
        missing.append('AZURE_OPENAI_ENDPOINT')
    
    if not config['deployment'] or config['deployment'] == 'gpt-4o-cv-analysis':
        missing.append('AZURE_OPENAI_DEPLOYMENT')
    
    if not config['api_version']:
        missing.append('AZURE_OPENAI_API_VERSION')
    
    return missing

def test_connection(config):
    """Prueba la conexión con Azure OpenAI"""
    try:
        print("🔧 Probando conexión con Azure OpenAI...")
        
        client = AzureOpenAI(
            api_key=config['api_key'],
            api_version=config['api_version'],
            azure_endpoint=config['endpoint'],
            timeout=30.0
        )
        
        # Probar con un prompt simple
        response = client.chat.completions.create(
            model=config['deployment'],
            messages=[
                {"role": "user", "content": "Responde solo 'OK' si puedes leer este mensaje."}
            ],
            max_tokens=10,
            temperature=0
        )
        
        result = response.choices[0].message.content.strip()
        if result == "OK":
            print("✅ Conexión exitosa con Azure OpenAI")
            return True
        else:
            print(f"⚠️ Respuesta inesperada: {result}")
            return False
            
    except Exception as e:
        print(f"❌ Error de conexión: {str(e)}")
        return False

def list_available_models(config):
    """Lista los modelos disponibles en el deployment"""
    try:
        print("📋 Verificando modelos disponibles...")
        
        client = AzureOpenAI(
            api_key=config['api_key'],
            api_version=config['api_version'],
            azure_endpoint=config['endpoint'],
            timeout=30.0
        )
        
        # Intentar obtener información del deployment
        response = client.chat.completions.create(
            model=config['deployment'],
            messages=[
                {"role": "user", "content": "Hola"}
            ],
            max_tokens=5
        )
        
        print("✅ El deployment está funcionando correctamente")
        return True
        
    except Exception as e:
        print(f"❌ Error con el deployment '{config['deployment']}': {str(e)}")
        return False

def main():
    """Función principal"""
    print("🚀 Configuración de Azure OpenAI para EvaluaTE")
    print("=" * 50)
    
    # Verificar archivo .env
    if not check_env_file():
        sys.exit(1)
    
    # Cargar configuración
    config = load_config()
    
    # Validar configuración
    missing = validate_config(config)
    if missing:
        print(f"❌ Faltan variables de configuración: {', '.join(missing)}")
        print("\n📝 Para configurar Azure OpenAI:")
        print("1. Ve a https://portal.azure.com")
        print("2. Crea un recurso 'Azure OpenAI'")
        print("3. Ve a 'Keys and Endpoint' y copia la Key 1")
        print("4. Copia el Endpoint")
        print("5. Ve a 'Model deployments' y crea un deployment")
        print("6. Actualiza el archivo .env con los valores reales")
        sys.exit(1)
    
    print("✅ Configuración básica válida")
    print(f"   Endpoint: {config['endpoint']}")
    print(f"   Deployment: {config['deployment']}")
    print(f"   API Version: {config['api_version']}")
    
    # Probar conexión
    if not test_connection(config):
        print("\n❌ No se pudo conectar con Azure OpenAI")
        print("Verifica que:")
        print("1. La API Key sea correcta")
        print("2. El Endpoint sea válido")
        print("3. Tengas permisos para usar el servicio")
        sys.exit(1)
    
    # Verificar deployment
    if not list_available_models(config):
        print(f"\n❌ El deployment '{config['deployment']}' no está disponible")
        print("Para solucionarlo:")
        print("1. Ve a tu recurso de Azure OpenAI en Azure Portal")
        print("2. Ve a 'Model deployments'")
        print("3. Crea un nuevo deployment con un modelo disponible")
        print("4. Usa uno de estos nombres comunes:")
        print("   - gpt-35-turbo")
        print("   - gpt-4")
        print("   - gpt-4o")
        print("5. Actualiza AZURE_OPENAI_DEPLOYMENT en .env")
        sys.exit(1)
    
    print("\n🎉 ¡Configuración completada exitosamente!")
    print("La aplicación está lista para generar informes con IA.")

if __name__ == "__main__":
    main()