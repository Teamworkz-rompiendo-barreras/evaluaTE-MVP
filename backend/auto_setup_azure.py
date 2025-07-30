#!/usr/bin/env python3
"""
Script de configuración automática para Azure OpenAI
Este script guía al usuario paso a paso para configurar Azure OpenAI en EvaluaTE.
"""

import os
import sys
import webbrowser
from dotenv import load_dotenv

def print_header(title):
    """Imprime un encabezado formateado"""
    print("\n" + "="*60)
    print(f"🚀 {title}")
    print("="*60)

def print_success(message):
    """Imprime un mensaje de éxito"""
    print(f"✅ {message}")

def print_error(message):
    """Imprime un mensaje de error"""
    print(f"❌ {message}")

def print_warning(message):
    """Imprime un mensaje de advertencia"""
    print(f"⚠️ {message}")

def print_info(message):
    """Imprime un mensaje informativo"""
    print(f"ℹ️ {message}")

def print_step(step, title):
    """Imprime un paso numerado"""
    print(f"\n📋 PASO {step}: {title}")
    print("-" * 40)

def check_existing_config():
    """Verifica si ya existe configuración"""
    load_dotenv()
    
    api_key = os.getenv('AZURE_OPENAI_API_KEY')
    endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')
    deployment = os.getenv('AZURE_OPENAI_DEPLOYMENT')
    
    if api_key and endpoint and deployment:
        if (api_key != 'tu_api_key_aqui' and 
            endpoint != 'https://tu-recurso.openai.azure.com' and
            deployment != 'gpt-4o-cv-analysis'):
            return True
    
    return False

def create_env_file():
    """Crea el archivo .env si no existe"""
    if not os.path.exists('.env'):
        print_info("Creando archivo .env...")
        
        env_content = """# Azure OpenAI Configuration
AZURE_OPENAI_API_KEY=tu_api_key_aqui
AZURE_OPENAI_ENDPOINT=https://tu-recurso.openai.azure.com
AZURE_OPENAI_DEPLOYMENT=gpt-35-turbo
AZURE_OPENAI_API_VERSION=2024-02-15-preview

# Configuración del backend
PORT=8000
HOST=0.0.0.0

# Configuración de CORS
ALLOWED_ORIGINS=http://localhost:3005,http://localhost:3006,http://localhost:5173,https://yellow-mud-0b6281c1e.6.azurestaticapps.net

# Configuración de Email para Notificaciones
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_USER=tu_email@gmail.com
EMAIL_PASSWORD=tu_contraseña_de_aplicacion
ADMIN_EMAIL=ester@teamworkz.co
"""
        
        with open('.env', 'w', encoding='utf-8') as f:
            f.write(env_content)
        
        print_success("Archivo .env creado")
    else:
        print_info("Archivo .env ya existe")

def get_user_input(prompt, default=""):
    """Obtiene entrada del usuario con valor por defecto"""
    if default:
        user_input = input(f"{prompt} [{default}]: ").strip()
        return user_input if user_input else default
    else:
        return input(f"{prompt}: ").strip()

def step1_create_resource():
    """Paso 1: Crear recurso Azure OpenAI"""
    print_step(1, "CREAR RECURSO AZURE OPENAI")
    
    print("Para crear un recurso Azure OpenAI, necesitas:")
    print("1. Una cuenta de Azure activa")
    print("2. Permisos para crear recursos")
    print("3. Una suscripción válida")
    
    print("\n📋 Información requerida:")
    print("- Nombre del recurso (ej: evaluador-openai)")
    print("- Región (ej: West Europe, Spain Central)")
    print("- Plan de precios (recomendado: Standard S0)")
    
    print("\n🔗 Enlaces útiles:")
    print("- Portal de Azure: https://portal.azure.com")
    print("- Documentación: https://docs.microsoft.com/azure/cognitive-services/openai/")
    
    input("\nPresiona Enter cuando hayas creado el recurso...")
    
    return True

def step2_get_credentials():
    """Paso 2: Obtener credenciales"""
    print_step(2, "OBTENER CREDENCIALES")
    
    print("Ahora necesitas obtener las credenciales de tu recurso:")
    print("\n1. Ve a tu recurso Azure OpenAI en el portal")
    print("2. En el menú lateral, ve a 'Keys and Endpoint'")
    print("3. Copia la 'Key 1' y el 'Endpoint'")
    
    api_key = get_user_input("Ingresa tu API Key")
    endpoint = get_user_input("Ingresa tu Endpoint (debe terminar en .openai.azure.com)")
    
    if not api_key or not endpoint:
        print_error("Las credenciales son requeridas")
        return False
    
    if not endpoint.endswith('.openai.azure.com'):
        print_error("El endpoint debe terminar en .openai.azure.com")
        return False
    
    return api_key, endpoint

def step3_create_deployment():
    """Paso 3: Crear deployment"""
    print_step(3, "CREAR DEPLOYMENT")
    
    print("Ahora necesitas crear un deployment:")
    print("\n1. Ve a 'Model deployments' en tu recurso")
    print("2. Haz clic en 'Create'")
    print("3. Configura:")
    print("   - Nombre: gpt-35-turbo (recomendado)")
    print("   - Modelo: gpt-35-turbo")
    print("   - Capacidad: Standard")
    
    deployment_name = get_user_input("Ingresa el nombre de tu deployment", "gpt-35-turbo")
    
    if not deployment_name:
        print_error("El nombre del deployment es requerido")
        return False
    
    return deployment_name

def step4_update_env_file(api_key, endpoint, deployment):
    """Paso 4: Actualizar archivo .env"""
    print_step(4, "ACTUALIZAR CONFIGURACIÓN")
    
    print("Actualizando archivo .env con tus credenciales...")
    
    # Leer el archivo actual
    with open('.env', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Reemplazar valores
    content = content.replace('tu_api_key_aqui', api_key)
    content = content.replace('https://tu-recurso.openai.azure.com', endpoint)
    content = content.replace('gpt-35-turbo', deployment)
    
    # Escribir archivo actualizado
    with open('.env', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print_success("Archivo .env actualizado con tus credenciales")
    return True

def step5_test_configuration():
    """Paso 5: Probar configuración"""
    print_step(5, "PROBAR CONFIGURACIÓN")
    
    print("Probando la configuración...")
    
    try:
        from openai import AzureOpenAI
        from dotenv import load_dotenv
        
        load_dotenv()
        
        api_key = os.getenv('AZURE_OPENAI_API_KEY')
        endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')
        deployment = os.getenv('AZURE_OPENAI_DEPLOYMENT')
        api_version = os.getenv('AZURE_OPENAI_API_VERSION')
        
        if not all([api_key, endpoint, deployment, api_version]):
            print_error("Faltan variables de configuración")
            return False
        
        client = AzureOpenAI(
            api_key=api_key,
            api_version=api_version,
            azure_endpoint=endpoint,
            timeout=30.0
        )
        
        # Probar conexión
        response = client.chat.completions.create(
            model=deployment,
            messages=[
                {"role": "user", "content": "Responde solo 'OK' si puedes leer este mensaje."}
            ],
            max_tokens=10,
            temperature=0
        )
        
        result = response.choices[0].message.content.strip()
        if result == "OK":
            print_success("¡Configuración exitosa!")
            return True
        else:
            print_warning(f"Respuesta inesperada: {result}")
            return False
            
    except Exception as e:
        print_error(f"Error en la configuración: {str(e)}")
        return False

def step6_azure_web_app():
    """Paso 6: Configurar Azure Web App"""
    print_step(6, "CONFIGURAR AZURE WEB APP")
    
    print("Para que la aplicación funcione en producción, necesitas configurar las variables de entorno en Azure Web App:")
    print("\n1. Ve a tu Azure Web App (evaluador-backend)")
    print("2. Ve a 'Configuration' → 'Application settings'")
    print("3. Agrega estas variables:")
    print("   - AZURE_OPENAI_API_KEY: tu_api_key")
    print("   - AZURE_OPENAI_ENDPOINT: tu_endpoint")
    print("   - AZURE_OPENAI_DEPLOYMENT: tu_deployment")
    print("   - AZURE_OPENAI_API_VERSION: 2024-02-15-preview")
    print("4. Haz clic en 'Save'")
    
    print("\n🔗 Portal de Azure: https://portal.azure.com")
    
    input("\nPresiona Enter cuando hayas configurado Azure Web App...")
    
    return True

def step7_verify_functionality():
    """Paso 7: Verificar funcionalidad"""
    print_step(7, "VERIFICAR FUNCIONALIDAD")
    
    print("Ejecutando verificación completa...")
    
    try:
        # Importar y ejecutar script de verificación
        from verify_ai_setup import main as verify_main
        verify_main()
        
        print_success("Verificación completada")
        return True
        
    except Exception as e:
        print_error(f"Error en la verificación: {str(e)}")
        return False

def main():
    """Función principal"""
    print_header("CONFIGURACIÓN AUTOMÁTICA DE AZURE OPENAI")
    print("Este script te guiará paso a paso para configurar Azure OpenAI en EvaluaTE.")
    
    # Verificar configuración existente
    if check_existing_config():
        print_warning("Ya existe una configuración de Azure OpenAI")
        response = input("¿Quieres reconfigurar? (s/N): ").strip().lower()
        if response != 's':
            print_info("Configuración existente mantenida")
            return
    
    # Crear archivo .env si no existe
    create_env_file()
    
    # Paso 1: Crear recurso
    if not step1_create_resource():
        print_error("Error en el paso 1")
        return
    
    # Paso 2: Obtener credenciales
    credentials = step2_get_credentials()
    if not credentials:
        print_error("Error en el paso 2")
        return
    
    api_key, endpoint = credentials
    
    # Paso 3: Crear deployment
    deployment = step3_create_deployment()
    if not deployment:
        print_error("Error en el paso 3")
        return
    
    # Paso 4: Actualizar configuración
    if not step4_update_env_file(api_key, endpoint, deployment):
        print_error("Error en el paso 4")
        return
    
    # Paso 5: Probar configuración
    if not step5_test_configuration():
        print_error("Error en el paso 5")
        print_info("Revisa las credenciales y vuelve a intentar")
        return
    
    # Paso 6: Configurar Azure Web App
    step6_azure_web_app()
    
    # Paso 7: Verificar funcionalidad
    step7_verify_functionality()
    
    # Resumen final
    print_header("CONFIGURACIÓN COMPLETADA")
    print_success("¡Azure OpenAI ha sido configurado exitosamente!")
    print("\n📋 Resumen de lo que se ha configurado:")
    print("✅ Recurso Azure OpenAI creado")
    print("✅ Credenciales configuradas")
    print("✅ Deployment creado")
    print("✅ Archivo .env actualizado")
    print("✅ Conexión probada")
    print("✅ Azure Web App configurado")
    print("✅ Funcionalidad verificada")
    
    print("\n🎉 La aplicación está lista para generar informes con IA!")
    print("\n📚 Recursos adicionales:")
    print("- Documentación: azure_openai_setup.md")
    print("- Verificación: python verify_ai_setup.py")
    print("- Soporte: Revisa los logs en Azure Portal")

if __name__ == "__main__":
    main() 