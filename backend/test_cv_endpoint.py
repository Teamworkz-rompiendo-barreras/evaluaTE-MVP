#!/usr/bin/env python3
"""
Script para probar el endpoint de análisis de CV y verificar el flujo completo
"""

import os
import sys
import json
import requests
from pathlib import Path

# Agregar el directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_cv_analysis_endpoint():
    """Prueba el endpoint de análisis de CV"""
    print("🔍 Probando endpoint de análisis de CV...")
    
    # Buscar un archivo PDF de prueba
    pdf_files = list(Path('.').glob('*.pdf'))
    if not pdf_files:
        print("❌ No se encontraron archivos PDF para probar")
        return False
    
    test_pdf = pdf_files[0]
    print(f"📄 Usando archivo: {test_pdf}")
    
    # URL del endpoint
    url = "http://localhost:8000/api/pdf/analyze-cv"
    
    # Datos de prueba similares a los del frontend
    test_data = {
        'userId': 'test_user_123',
        'fullName': 'Esther Pérez',
        'softSkills': json.dumps([
            {'skill': 'Toma de decisiones', 'score': 40, 'level': 'Bajo', 'confidence': 40}
        ]),
        'jobPreferences': json.dumps({
            'areas': ['grabadora de datos'],
            'needs': ['Necesito flexibilidad horaria'],
            'workMode': 'remoto'
        }),
        'completedGames': json.dumps(['decision-making', 'analytical-thinking'])
    }
    
    try:
        # Enviar archivo y datos
        with open(test_pdf, 'rb') as f:
            files = {'file': (test_pdf.name, f, 'application/pdf')}
            
            print("📤 Enviando petición al endpoint...")
            response = requests.post(url, files=files, data=test_data, timeout=60)
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📊 Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Endpoint respondió correctamente")
            print(f"📊 Datos del CV extraídos: {len(result)} campos")
            
            # Verificar datos específicos
            if 'strengths' in result:
                print(f"✅ Fortalezas: {len(result['strengths'])} elementos")
            if 'weaknesses' in result:
                print(f"✅ Debilidades: {len(result['weaknesses'])} elementos")
            if 'skills' in result:
                print(f"✅ Habilidades: {len(result['skills'])} elementos")
            if 'education' in result:
                print(f"✅ Educación: {len(result['education'])} elementos")
            
            return True
        else:
            print(f"❌ Error en endpoint: {response.status_code}")
            print(f"Respuesta: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ No se pudo conectar al servidor. ¿Está ejecutándose?")
        print("Ejecuta: uvicorn main:app --reload --host 0.0.0.0 --port 8000")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

def test_ia_report_endpoint():
    """Prueba el endpoint de generación de informe IA"""
    print("\n📋 Probando endpoint de informe IA...")
    
    url = "http://localhost:8000/api/informe-ia"
    
    # Datos de prueba similares a los del frontend
    test_data = {
        'userId': 'test_user_123',
        'fullName': 'Esther Pérez',
        'softSkills': [
            {'skill': 'Toma de decisiones', 'score': 40, 'level': 'Bajo', 'confidence': 40}
        ],
        'cvAnalysis': {
            'strengths': ['Experiencia técnica'],
            'weaknesses': ['Falta de experiencia en gestión'],
            'feedback': 'CV bien estructurado',
            'structure': 'buena',
            'coherence': 'buena',
            'experience': 'regular',
            'skills': ['Python', 'JavaScript'],
            'education': ['Ingeniería Informática'],
            'alerts': []
        },
        'jobPreferences': {
            'areas': ['grabadora de datos'],
            'needs': ['Necesito flexibilidad horaria'],
            'workMode': 'remoto'
        },
        'completedGames': ['decision-making', 'analytical-thinking'],
        'logs': []
    }
    
    try:
        print("📤 Enviando petición al endpoint de IA...")
        response = requests.post(
            url, 
            json=test_data, 
            headers={'Content-Type': 'application/json'},
            timeout=120
        )
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Endpoint de IA respondió correctamente")
            
            if 'report' in result and 'informeProfesional' in result['report']:
                print("✅ Informe profesional generado correctamente")
                print(f"📄 Longitud del informe: {len(result['report']['informeProfesional'])} caracteres")
                
                # Verificar que el informe contenga datos del CV
                informe = result['report']['informeProfesional']
                if 'Python' in informe or 'JavaScript' in informe:
                    print("✅ El informe incluye datos del CV")
                else:
                    print("⚠️ El informe no parece incluir datos del CV")
                
                return True
            else:
                print("❌ No se generó el informe profesional")
                return False
        else:
            print(f"❌ Error en endpoint de IA: {response.status_code}")
            print(f"Respuesta: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ No se pudo conectar al servidor. ¿Está ejecutándose?")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

def check_backend_status():
    """Verifica si el backend está ejecutándose"""
    print("🔍 Verificando estado del backend...")
    
    try:
        response = requests.get("http://localhost:8000/", timeout=5)
        if response.status_code == 200:
            print("✅ Backend está ejecutándose")
            return True
        else:
            print(f"⚠️ Backend responde con status: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Backend no está ejecutándose")
        print("💡 Para iniciar el backend:")
        print("   cd backend")
        print("   source venv/bin/activate")
        print("   uvicorn main:app --reload --host 0.0.0.0 --port 8000")
        return False
    except Exception as e:
        print(f"❌ Error verificando backend: {e}")
        return False

def main():
    """Función principal"""
    print("🧪 Iniciando pruebas de endpoints...")
    print("=" * 60)
    
    # Verificar que el backend esté ejecutándose
    if not check_backend_status():
        return False
    
    tests = [
        ("Análisis de CV", test_cv_analysis_endpoint),
        ("Informe IA", test_ia_report_endpoint)
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
    
    # Resumen
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
        print("🎉 ¡Todos los endpoints funcionan correctamente!")
    else:
        print("⚠️ Algunos endpoints fallaron. Revisa los errores anteriores.")
    
    return passed == len(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 