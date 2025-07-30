#!/usr/bin/env python3
"""
Script de configuración para Azure AI Document Intelligence
Este script ayuda a configurar Azure AI Document Intelligence para mejorar la lectura de CVs.
"""

import os
import sys
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
    """Verifica si ya existe configuración de Document Intelligence"""
    load_dotenv()
    
    endpoint = os.getenv('AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT')
    key = os.getenv('AZURE_DOCUMENT_INTELLIGENCE_KEY')
    
    if endpoint and key:
        if (endpoint != 'https://tu-recurso-document-intelligence.cognitiveservices.azure.com/' and 
            key != 'tu_document_intelligence_key_aqui'):
            return True
    
    return False

def create_env_file():
    """Crea o actualiza el archivo .env"""
    env_file = '.env'
    env_content = ""
    
    # Leer archivo existente si existe
    if os.path.exists(env_file):
        with open(env_file, 'r', encoding='utf-8') as f:
            env_content = f.read()
    
    # Agregar configuración de Document Intelligence si no existe
    if 'AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT' not in env_content:
        env_content += """

# Azure AI Document Intelligence Configuration (OPCIONAL pero RECOMENDADO)
# Mejora significativamente la extracción de información de CVs
AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT=https://tu-recurso-document-intelligence.cognitiveservices.azure.com/
AZURE_DOCUMENT_INTELLIGENCE_KEY=tu_document_intelligence_key_aqui

# Azure Storage Configuration (OPCIONAL)
# Para almacenamiento de archivos temporales
AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=tu-cuenta;AccountKey=tu-clave;EndpointSuffix=core.windows.net
AZURE_STORAGE_CONTAINER=cv-uploads
"""
    
    # Escribir archivo actualizado
    with open(env_file, 'w', encoding='utf-8') as f:
        f.write(env_content)
    
    print_success("Archivo .env actualizado con configuración de Document Intelligence")

def step1_create_resource():
    """Paso 1: Crear recurso Azure AI Document Intelligence"""
    print_step(1, "CREAR RECURSO AZURE AI DOCUMENT INTELLIGENCE")
    
    print("Para crear un recurso Azure AI Document Intelligence:")
    print("1. Ve a https://portal.azure.com")
    print("2. Busca 'Document Intelligence' o 'Form Recognizer'")
    print("3. Haz clic en 'Crear'")
    print("4. Completa la información:")
    print("   - Suscripción: Tu suscripción de Azure")
    print("   - Grupo de recursos: Crea uno nuevo o usa existente")
    print("   - Región: Elige la más cercana a ti")
    print("   - Nombre del recurso: Ej: 'evaluaTE-document-intelligence'")
    print("   - Plan de precios: Free (F0) para pruebas, Standard (S0) para producción")
    print("5. Haz clic en 'Revisar + crear' y luego 'Crear'")
    
    input("\nPresiona Enter cuando hayas creado el recurso...")

def step2_get_credentials():
    """Paso 2: Obtener credenciales"""
    print_step(2, "OBTENER CREDENCIALES")
    
    print("Una vez creado el recurso:")
    print("1. Ve al recurso creado en Azure Portal")
    print("2. En el menú lateral, ve a 'Keys and Endpoint'")
    print("3. Copia la 'Key 1' y el 'Endpoint'")
    print("4. Los necesitarás en el siguiente paso")
    
    input("\nPresiona Enter cuando tengas las credenciales...")

def step3_update_env_file():
    """Paso 3: Actualizar archivo .env"""
    print_step(3, "ACTUALIZAR CONFIGURACIÓN")
    
    endpoint = input("Endpoint de Document Intelligence: ").strip()
    key = input("Key de Document Intelligence: ").strip()
    
    if not endpoint or not key:
        print_error("Las credenciales son requeridas")
        return False
    
    # Validar formato del endpoint
    if not endpoint.startswith('https://') or not endpoint.endswith('.cognitiveservices.azure.com/'):
        print_warning("El endpoint debe tener el formato: https://tu-recurso.cognitiveservices.azure.com/")
    
    # Actualizar archivo .env
    env_file = '.env'
    if os.path.exists(env_file):
        with open(env_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Reemplazar valores
        content = content.replace(
            'AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT=https://tu-recurso-document-intelligence.cognitiveservices.azure.com/',
            f'AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT={endpoint}'
        )
        content = content.replace(
            'AZURE_DOCUMENT_INTELLIGENCE_KEY=tu_document_intelligence_key_aqui',
            f'AZURE_DOCUMENT_INTELLIGENCE_KEY={key}'
        )
        
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print_success("Configuración actualizada en .env")
        return True
    else:
        print_error("Archivo .env no encontrado. Ejecuta primero el setup de Azure OpenAI")
        return False

def step4_test_configuration():
    """Paso 4: Probar configuración"""
    print_step(4, "PROBAR CONFIGURACIÓN")
    
    try:
        # Cargar variables de entorno
        load_dotenv()
        
        endpoint = os.getenv('AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT')
        key = os.getenv('AZURE_DOCUMENT_INTELLIGENCE_KEY')
        
        if not endpoint or not key:
            print_error("Configuración incompleta")
            return False
        
        # Intentar importar y configurar
        try:
            from azure.ai.formrecognizer import DocumentAnalysisClient
            from azure.core.credentials import AzureKeyCredential
            
            client = DocumentAnalysisClient(
                endpoint=endpoint,
                credential=AzureKeyCredential(key)
            )
            
            print_success("✅ Conexión exitosa con Azure AI Document Intelligence")
            print_info("El servicio está listo para analizar CVs")
            return True
            
        except ImportError:
            print_error("No se pudo importar azure-ai-formrecognizer")
            print_info("Instala las dependencias: pip install azure-ai-formrecognizer")
            return False
            
        except Exception as e:
            print_error(f"Error de conexión: {str(e)}")
            print_info("Verifica las credenciales y el endpoint")
            return False
            
    except Exception as e:
        print_error(f"Error en prueba: {str(e)}")
        return False

def step5_install_dependencies():
    """Paso 5: Instalar dependencias"""
    print_step(5, "INSTALAR DEPENDENCIAS")
    
    print("Instalando dependencias necesarias...")
    
    try:
        import subprocess
        result = subprocess.run([
            sys.executable, '-m', 'pip', 'install', 
            'azure-ai-formrecognizer==3.4.0',
            'azure-storage-blob==12.19.0'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print_success("✅ Dependencias instaladas correctamente")
            return True
        else:
            print_error(f"Error instalando dependencias: {result.stderr}")
            return False
            
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False

def main():
    """Función principal"""
    print_header("CONFIGURACIÓN DE AZURE AI DOCUMENT INTELLIGENCE")
    
    print_info("Este script te ayudará a configurar Azure AI Document Intelligence")
    print_info("para mejorar significativamente la lectura de CVs en EvaluaTE.")
    print_info("")
    print_info("Document Intelligence es un servicio de Azure que:")
    print_info("- Extrae texto e información estructurada de documentos")
    print_info("- Reconoce automáticamente secciones de CVs")
    print_info("- Identifica habilidades, experiencia, educación, etc.")
    print_info("- Es mucho más preciso que OCR tradicional")
    
    # Verificar configuración existente
    if check_existing_config():
        print_warning("Ya existe configuración de Document Intelligence")
        response = input("¿Quieres reconfigurar? (s/n): ").lower()
        if response != 's':
            print_info("Configuración existente mantenida")
            return
    
    # Crear archivo .env si no existe
    create_env_file()
    
    # Pasos de configuración
    if not step1_create_resource():
        return
    
    if not step2_get_credentials():
        return
    
    if not step3_update_env_file():
        return
    
    if not step5_install_dependencies():
        return
    
    if not step4_test_configuration():
        return
    
    print_header("CONFIGURACIÓN COMPLETADA")
    print_success("Azure AI Document Intelligence está configurado correctamente")
    print_info("")
    print_info("Beneficios que obtendrás:")
    print_info("✅ Mejor extracción de información de CVs")
    print_info("✅ Reconocimiento automático de secciones")
    print_info("✅ Identificación precisa de habilidades técnicas")
    print_info("✅ Extracción de experiencia laboral estructurada")
    print_info("✅ Análisis de formación académica")
    print_info("")
    print_info("La aplicación ahora usará Document Intelligence como método principal")
    print_info("para analizar CVs, con fallback al método tradicional si es necesario.")

if __name__ == "__main__":
    main() 