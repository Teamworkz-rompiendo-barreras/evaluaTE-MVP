#!/usr/bin/env python3
"""
Script de prueba para verificar que el análisis de CV funcione correctamente
y que los datos lleguen al informe final
"""

import os
import sys
import json
from pathlib import Path

# Agregar el directorio actual al path para importaciones
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_cv_analysis():
    """Prueba el análisis de CV"""
    print("🔍 Probando análisis de CV...")
    
    try:
        from cv_analyzer import extract_pdf_info
        
        # Buscar un archivo PDF de prueba
        pdf_files = list(Path('.').glob('*.pdf'))
        if not pdf_files:
            print("❌ No se encontraron archivos PDF para probar")
            return False
        
        test_pdf = pdf_files[0]
        print(f"📄 Usando archivo de prueba: {test_pdf}")
        
        # Analizar el CV
        cv_data = extract_pdf_info(str(test_pdf))
        
        if not cv_data:
            print("❌ No se pudo extraer información del CV")
            return False
        
        print("✅ Análisis de CV exitoso")
        print(f"📊 Datos extraídos: {len(cv_data)} campos")
        
        # Mostrar algunos datos clave
        if 'text' in cv_data:
            print(f"📝 Texto extraído: {len(cv_data['text'])} caracteres")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en análisis de CV: {e}")
        return False

def test_report_generation():
    """Prueba la generación de informes"""
    print("\n📋 Probando generación de informes...")
    
    try:
        from generate_report import generar_informe
        
        # Datos de prueba
        test_data = {
            'fullName': 'Usuario de Prueba',
            'softSkills': [
                {'skill': 'Comunicación', 'score': 85, 'level': 'alto'},
                {'skill': 'Trabajo en equipo', 'score': 70, 'level': 'medio'}
            ],
            'cvAnalysis': {
                'strengths': ['Experiencia técnica sólida'],
                'weaknesses': ['Falta de experiencia en gestión'],
                'skills': ['Python', 'JavaScript', 'SQL']
            }
        }
        
        # Formatear datos para el informe
        perfil = f"""
DATOS DEL CANDIDATO:
Nombre: {test_data['fullName']}

HABILIDADES SOFT EVALUADAS:
{json.dumps(test_data['softSkills'], indent=2, ensure_ascii=False)}

ANÁLISIS DETALLADO DEL CV:
{json.dumps(test_data['cvAnalysis'], indent=2, ensure_ascii=False)}
"""
        
        # Generar informe
        informe = generar_informe(perfil)
        
        if not informe:
            print("❌ No se pudo generar el informe")
            return False
        
        print("✅ Generación de informe exitosa")
        print(f"📄 Longitud del informe: {len(informe)} caracteres")
        
        # Verificar que el informe contenga datos del CV
        if 'Experiencia técnica sólida' in informe:
            print("✅ El informe incluye datos del análisis de CV")
        else:
            print("⚠️ El informe no parece incluir datos del CV")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en generación de informe: {e}")
        return False

def test_main_endpoint():
    """Prueba el endpoint principal de análisis de CV"""
    print("\n🌐 Probando endpoint de análisis de CV...")
    
    try:
        from main import app
        from fastapi.testclient import TestClient
        
        client = TestClient(app=app)
        
        # Buscar un archivo PDF de prueba
        pdf_files = list(Path('.').glob('*.pdf'))
        if not pdf_files:
            print("❌ No se encontraron archivos PDF para probar")
            return False
        
        test_pdf = pdf_files[0]
        
        # Simular datos de formulario
        test_data = {
            'userId': 'test_user_123',
            'fullName': 'Usuario de Prueba',
            'softSkills': json.dumps([
                {'skill': 'Comunicación', 'score': 85, 'level': 'alto'}
            ]),
            'jobPreferences': json.dumps({
                'areas': ['Desarrollo de software'],
                'needs': ['Flexibilidad horaria']
            }),
            'completedGames': json.dumps(['game1', 'game2'])
        }
        
        # Crear archivo de prueba
        with open(test_pdf, 'rb') as f:
            files = {'file': (test_pdf.name, f, 'application/pdf')}
            
            response = client.post(
                "/api/pdf/analyze-cv",
                files=files,
                data=test_data
            )
        
        if response.status_code == 200:
            print("✅ Endpoint de análisis de CV funciona correctamente")
            result = response.json()
            print(f"📊 Respuesta: {len(result)} campos")
            return True
        else:
            print(f"❌ Error en endpoint: {response.status_code}")
            print(f"Respuesta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error en prueba de endpoint: {e}")
        return False

def main():
    """Función principal de pruebas"""
    print("🧪 Iniciando pruebas de funcionalidad CV...")
    print("=" * 60)
    
    # Verificar que el entorno virtual esté activado
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("⚠️ Advertencia: El entorno virtual no parece estar activado")
        print("Ejecuta: source venv/bin/activate")
    
    tests = [
        ("Análisis de CV", test_cv_analysis),
        ("Generación de Informes", test_report_generation),
        ("Endpoint de Análisis", test_main_endpoint)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Error inesperado en {test_name}: {e}")
            results.append((test_name, False))
    
    # Resumen de resultados
    print(f"\n{'='*60}")
    print("📊 RESUMEN DE PRUEBAS")
    print("=" * 60)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASÓ" if result else "❌ FALLÓ"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nResultado: {passed}/{len(results)} pruebas pasaron")
    
    if passed == len(results):
        print("🎉 ¡Todas las pruebas pasaron! El sistema está funcionando correctamente.")
    else:
        print("⚠️ Algunas pruebas fallaron. Revisa los errores anteriores.")
    
    return passed == len(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 