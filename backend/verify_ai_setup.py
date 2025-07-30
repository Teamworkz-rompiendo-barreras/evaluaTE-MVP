#!/usr/bin/env python3
"""
Script de verificación completa para Azure OpenAI y análisis de CV
Este script prueba todas las funcionalidades de IA implementadas en EvaluaTE.
"""

import os
import json
import sys
import requests
from datetime import datetime
from dotenv import load_dotenv

def print_header(title):
    """Imprime un encabezado formateado"""
    print("\n" + "="*60)
    print(f"🔍 {title}")
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

def check_env_file():
    """Verifica si existe el archivo .env"""
    if not os.path.exists('.env'):
        print_error("No se encontró el archivo .env")
        print_info("Copia env.example a .env y configura las variables:")
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
        'api_version': os.getenv('AZURE_OPENAI_API_VERSION'),
        'port': os.getenv('PORT', '8000'),
        'host': os.getenv('HOST', '0.0.0.0')
    }
    
    return config

def validate_config(config):
    """Valida la configuración básica"""
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

def test_azure_openai_connection(config):
    """Prueba la conexión con Azure OpenAI"""
    try:
        print_info("Probando conexión con Azure OpenAI...")
        
        from openai import AzureOpenAI
        
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
            print_success("Conexión exitosa con Azure OpenAI")
            return True
        else:
            print_warning(f"Respuesta inesperada: {result}")
            return False
            
    except Exception as e:
        print_error(f"Error de conexión: {str(e)}")
        return False

def test_cv_analyzer():
    """Prueba el módulo de análisis de CV"""
    try:
        print_info("Probando módulo de análisis de CV...")
        
        from cv_analyzer import extract_pdf_info, analyze_cv_with_ai
        
        # Crear un CV de prueba simple
        test_cv_text = """
        Juan Pérez
        juan.perez@email.com
        +34 123 456 789
        
        EXPERIENCIA LABORAL
        Desarrollador Frontend - TechCorp (2020-2023)
        - Desarrollo de aplicaciones web con React
        - Optimización de rendimiento
        - Trabajo en equipo con metodología Agile
        
        EDUCACIÓN
        Grado en Informática - Universidad de Madrid (2016-2020)
        
        HABILIDADES
        JavaScript, React, HTML, CSS, Git
        """
        
        # Probar análisis con IA
        result = analyze_cv_with_ai(test_cv_text)
        
        if result.get("error"):
            print_warning(f"Análisis de CV con IA: {result['error']}")
            return False
        else:
            print_success("Análisis de CV con IA funcionando correctamente")
            return True
            
    except Exception as e:
        print_error(f"Error en análisis de CV: {str(e)}")
        return False

def test_report_generation():
    """Prueba la generación de informes"""
    try:
        print_info("Probando generación de informes...")
        
        from generate_report import generar_informe
        
        # Datos de prueba
        test_profile = """
        DATOS DEL CANDIDATO:
        Nombre: María García
        ID de Usuario: test123
        
        HABILIDADES SOFT EVALUADAS:
        - Comunicación: 85%
        - Trabajo en equipo: 90%
        - Resolución de problemas: 75%
        
        ANÁLISIS DETALLADO DEL CV:
        CV bien estructurado con experiencia en desarrollo web.
        
        PREFERENCIAS LABORALES:
        Áreas: Tecnología, Desarrollo
        Necesidades: Flexibilidad, Entorno inclusivo
        """
        
        # Generar informe
        report = generar_informe(test_profile)
        
        if report and len(report) > 100:
            print_success("Generación de informes funcionando correctamente")
            return True
        else:
            print_warning("Informe generado pero parece incompleto")
            return False
            
    except Exception as e:
        print_error(f"Error en generación de informes: {str(e)}")
        return False

def test_backend_endpoints():
    """Prueba los endpoints del backend"""
    try:
        print_info("Probando endpoints del backend...")
        
        # Cargar configuración
        load_dotenv()
        host = os.getenv('HOST', '0.0.0.0')
        port = os.getenv('PORT', '8000')
        
        base_url = f"http://{host}:{port}"
        
        # Probar endpoint raíz
        response = requests.get(f"{base_url}/", timeout=10)
        if response.status_code == 200:
            print_success("Endpoint raíz funcionando")
        else:
            print_warning(f"Endpoint raíz: {response.status_code}")
        
        # Probar endpoint de informe IA
        test_data = {
            "userId": "test_verification",
            "fullName": "Usuario de Verificación",
            "softSkills": [
                {
                    "skill": "Comunicación",
                    "score": 85,
                    "level": "alto",
                    "confidence": 90
                }
            ],
            "completedGames": []
        }
        
        response = requests.post(
            f"{base_url}/api/informe-ia",
            json=test_data,
            timeout=30
        )
        
        if response.status_code == 200:
            print_success("Endpoint de informe IA funcionando")
            return True
        else:
            print_warning(f"Endpoint de informe IA: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print_warning(f"No se pudo conectar al backend: {str(e)}")
        return False
    except Exception as e:
        print_error(f"Error probando endpoints: {str(e)}")
        return False

def test_ocr_functionality():
    """Prueba la funcionalidad de OCR"""
    try:
        print_info("Verificando funcionalidad de OCR...")
        
        # Verificar dependencias
        try:
            import pytesseract
            from PIL import Image
            print_success("Dependencias de OCR instaladas")
            return True
        except ImportError:
            print_warning("OCR no disponible - instala pytesseract y Pillow")
            return False
            
    except Exception as e:
        print_error(f"Error verificando OCR: {str(e)}")
        return False

def test_document_intelligence():
    """Prueba Azure AI Document Intelligence"""
    try:
        print_info("Verificando Azure AI Document Intelligence...")
        
        # Verificar configuración
        endpoint = os.getenv('AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT')
        key = os.getenv('AZURE_DOCUMENT_INTELLIGENCE_KEY')
        
        if not endpoint or not key:
            print_warning("Document Intelligence no configurado")
            return False
        
        # Intentar importar y configurar
        try:
            from azure.ai.formrecognizer import DocumentAnalysisClient
            from azure.core.credentials import AzureKeyCredential
            
            client = DocumentAnalysisClient(
                endpoint=endpoint,
                credential=AzureKeyCredential(key)
            )
            
            print_success("Document Intelligence configurado correctamente")
            return True
            
        except ImportError:
            print_warning("Document Intelligence no disponible (dependencias no instaladas)")
            return False
            
        except Exception as e:
            print_error(f"Error en Document Intelligence: {str(e)}")
            return False
            
    except Exception as e:
        print_error(f"Error probando Document Intelligence: {str(e)}")
        return False

def generate_test_report():
    """Genera un reporte de verificación"""
    print_header("REPORTE DE VERIFICACIÓN")
    
    report = {
        "fecha": datetime.now().isoformat(),
        "configuracion": {},
        "pruebas": {},
        "recomendaciones": []
    }
    
    # Verificar configuración
    if check_env_file():
        config = load_config()
        missing = validate_config(config)
        
        report["configuracion"] = {
            "archivo_env": True,
            "variables_faltantes": missing,
            "azure_configurado": len(missing) == 0
        }
        
        if len(missing) == 0:
            print_success("Configuración básica válida")
            
            # Probar conexión Azure OpenAI
            azure_ok = test_azure_openai_connection(config)
            report["pruebas"]["azure_connection"] = azure_ok
            
            # Probar análisis de CV
            cv_ok = test_cv_analyzer()
            report["pruebas"]["cv_analysis"] = cv_ok
            
            # Probar generación de informes
            report_ok = test_report_generation()
            report["pruebas"]["report_generation"] = report_ok
            
            # Probar endpoints
            endpoints_ok = test_backend_endpoints()
            report["pruebas"]["endpoints"] = endpoints_ok
            
            # Probar OCR
            ocr_ok = test_ocr_functionality()
            report["pruebas"]["ocr"] = ocr_ok
            
            # Probar Document Intelligence
            doc_intelligence_ok = test_document_intelligence()
            report["pruebas"]["document_intelligence"] = doc_intelligence_ok
            
            # Generar recomendaciones
            if not azure_ok:
                report["recomendaciones"].append("Configurar Azure OpenAI correctamente")
            if not cv_ok:
                report["recomendaciones"].append("Revisar configuración del análisis de CV")
            if not report_ok:
                report["recomendaciones"].append("Verificar generación de informes")
            if not endpoints_ok:
                report["recomendaciones"].append("Revisar endpoints del backend")
            if not ocr_ok:
                report["recomendaciones"].append("Instalar dependencias de OCR")
            if not doc_intelligence_ok:
                report["recomendaciones"].append("Configurar Azure AI Document Intelligence para mejor análisis de CVs")
                
        else:
            print_error(f"Faltan variables de configuración: {', '.join(missing)}")
            report["recomendaciones"].append("Completar configuración de Azure OpenAI")
    else:
        report["configuracion"]["archivo_env"] = False
        report["recomendaciones"].append("Crear archivo .env con la configuración")
    
    # Guardar reporte
    with open("verification_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print_success("Reporte de verificación guardado en verification_report.json")
    
    return report

def main():
    """Función principal"""
    print_header("VERIFICACIÓN COMPLETA DE AZURE OPENAI Y ANÁLISIS DE CV")
    print("Este script verifica todas las funcionalidades de IA implementadas.")
    
    # Generar reporte
    report = generate_test_report()
    
    # Resumen final
    print_header("RESUMEN DE VERIFICACIÓN")
    
    if report["configuracion"]["azure_configurado"]:
        pruebas_exitosas = sum(report["pruebas"].values())
        total_pruebas = len(report["pruebas"])
        
        print(f"✅ Configuración: {pruebas_exitosas}/{total_pruebas} pruebas exitosas")
        
        if pruebas_exitosas == total_pruebas:
            print_success("¡Todas las funcionalidades están funcionando correctamente!")
            print_info("La aplicación está lista para generar informes con IA.")
        else:
            print_warning("Algunas funcionalidades necesitan atención.")
            print("Revisa las recomendaciones en el reporte.")
    else:
        print_error("Azure OpenAI no está configurado correctamente.")
        print("Sigue las instrucciones en azure_openai_setup.md")
    
    if report["recomendaciones"]:
        print_header("RECOMENDACIONES")
        for i, rec in enumerate(report["recomendaciones"], 1):
            print(f"{i}. {rec}")

if __name__ == "__main__":
    main() 