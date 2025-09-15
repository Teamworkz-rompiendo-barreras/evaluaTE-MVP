#!/usr/bin/env python3
"""
Test completo del flujo de la aplicación EvaluaTE
Verifica el funcionamiento del backend y la comunicación con el frontend
"""

import requests
import json
import time
import sys
from typing import Dict, Any

# Configuración
BACKEND_URL = "http://localhost:8080"
FRONTEND_URL = "http://localhost:5173"

def test_backend_health():
    """Prueba la salud del backend"""
    print("🔍 Probando salud del backend...")
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Backend saludable: {data}")
            return True
        else:
            print(f"❌ Backend no saludable: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error conectando al backend: {e}")
        return False

def test_backend_root():
    """Prueba la ruta raíz del backend"""
    print("🔍 Probando ruta raíz del backend...")
    try:
        response = requests.get(f"{BACKEND_URL}/", timeout=10)
        print(f"✅ Ruta raíz del backend responde: {response.status_code}")
        return True
    except Exception as e:
        print(f"❌ Error en ruta raíz del backend: {e}")
        return False

def test_frontend_health():
    """Prueba la salud del frontend"""
    print("🔍 Probando salud del frontend...")
    try:
        response = requests.get(f"{FRONTEND_URL}/", timeout=10)
        if response.status_code == 200:
            print("✅ Frontend responde correctamente")
            return True
        else:
            print(f"❌ Frontend no responde: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error conectando al frontend: {e}")
        return False

def test_api_informe_ia():
    """Prueba la API de generación de informes"""
    print("🔍 Probando API de generación de informes...")
    
    # Datos de prueba
    test_data = {
        "userId": "test-user-complete-flow",
        "fullName": "María García López",
        "softSkills": [
            {"skill": "Comunicación", "score": 90, "level": "Avanzado"},
            {"skill": "Trabajo en equipo", "score": 85, "level": "Avanzado"},
            {"skill": "Liderazgo", "score": 75, "level": "Intermedio"},
            {"skill": "Resolución de problemas", "score": 88, "level": "Avanzado"},
            {"skill": "Adaptabilidad", "score": 82, "level": "Intermedio"}
        ],
        "cvAnalysis": {
            "structure_score": 5,
            "coherence_score": 4,
            "key_info_score": 5,
            "clarity_score": 5,
            "style_score": 5,
            "evidence": {
                "structure": "Experiencia técnica sólida en desarrollo web",
                "coherence": "CV excelentemente estructurado",
                "key_info": "Portfolio de proyectos demostrable",
                "clarity": "Información clara",
                "style": "Presentación profesional"
            },
            "corrections": [],
            "reordering_suggestions": []
        },
        "jobPreferences": {
            "areas": ["Desarrollo de software", "Tecnología", "Startups", "Empresas de producto"],
            "needs": ["Crecimiento profesional", "Trabajo remoto", "Proyectos desafiantes"],
            "workMode": "Híbrido",
            "availability": "Inmediata",
            "willingToRelocate": True,
            "hasDisabilityCert": False
        },
        "completedGames": [
            "Evaluación de comunicación",
            "Test de trabajo en equipo",
            "Análisis de liderazgo",
            "Evaluación de resolución de problemas"
        ]
    }
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/informe-ia",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ API de informes funciona correctamente")
            print(f"📊 Resumen del informe: {data.get('summary', 'No disponible')}")
            print(f"👤 Datos personales: {data.get('personal_data', {}).get('name', 'No disponible')}")
            print(f"💪 Fortalezas: {len(data.get('strengths', []))} identificadas")
            print(f"📈 Áreas de mejora: {len(data.get('improvement_areas', []))} identificadas")
            print(f"🎯 Plan de acción: {len(data.get('action_plan', {}).get('short_term', []))} acciones a corto plazo")
            
            # Verificar estructura del informe
            required_fields = [
                'summary', 'personal_data', 'profile_summary', 'cv_summary', 'cv_details',
                'strengths', 'improvement_areas', 'cv_analysis', 'action_plan'
            ]
            
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                print(f"⚠️ Campos faltantes en el informe: {missing_fields}")
            else:
                print("✅ Estructura del informe completa")
            
            return True, data
        else:
            print(f"❌ Error en API de informes: {response.status_code}")
            print(f"Respuesta: {response.text}")
            return False, None
            
    except Exception as e:
        print(f"❌ Error probando API de informes: {e}")
        return False, None

def test_api_pdf_generation():
    """Prueba la generación de PDFs"""
    print("🔍 Probando generación de PDFs...")
    
    # Usar los mismos datos de prueba
    test_data = {
        "userId": "test-user-complete-flow",
        "fullName": "María García López",
        "softSkills": [
            {"skill": "Comunicación", "score": 90, "level": "Avanzado"},
            {"skill": "Trabajo en equipo", "score": 85, "level": "Avanzado"}
        ],
        "cvAnalysis": {
            "structure_score": 4,
            "coherence_score": 4,
            "key_info_score": 4,
            "clarity_score": 4,
            "style_score": 4,
            "evidence": {
                "structure": "CV bien estructurado",
                "coherence": "",
                "key_info": "Experiencia técnica sólida",
                "clarity": "",
                "style": ""
            },
            "corrections": [],
            "reordering_suggestions": []
        },
        "jobPreferences": {
            "areas": ["Desarrollo de software"]
        }
    }
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/pdf/generate-report",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            content_type = response.headers.get('content-type', '')
            if 'application/pdf' in content_type:
                print("✅ Generación de PDF funciona correctamente")
                print(f"📄 Tamaño del PDF: {len(response.content)} bytes")
                return True
            else:
                print(f"⚠️ Respuesta no es PDF: {content_type}")
                return False
        else:
            print(f"❌ Error generando PDF: {response.status_code}")
            print(f"Respuesta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error probando generación de PDF: {e}")
        return False

def test_frontend_backend_integration():
    """Prueba la integración entre frontend y backend"""
    print("🔍 Probando integración frontend-backend...")
    
    # Simular una petición como la haría el frontend
    test_data = {
        "userId": "frontend-test-user",
        "fullName": "Carlos Rodríguez",
        "softSkills": [
            {"skill": "Creatividad", "score": 95, "level": "Avanzado"},
            {"skill": "Innovación", "score": 88, "level": "Avanzado"}
        ],
        "cvAnalysis": {
            "structure_score": 4,
            "coherence_score": 4,
            "key_info_score": 4,
            "clarity_score": 4,
            "style_score": 4,
            "evidence": {
                "structure": "Excelente perfil para roles creativos",
                "coherence": "",
                "key_info": "Perfil creativo e innovador",
                "clarity": "",
                "style": ""
            },
            "corrections": [],
            "reordering_suggestions": []
        },
        "jobPreferences": {
            "areas": ["Diseño", "Creatividad", "Innovación"]
        }
    }
    
    try:
        # Simular la petición del frontend
        response = requests.post(
            f"{BACKEND_URL}/api/informe-ia",
            json=test_data,
            headers={
                "Content-Type": "application/json",
                "User-Agent": "EvaluaTE-Frontend/1.0",
                "Origin": FRONTEND_URL
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Integración frontend-backend funciona correctamente")
            print(f"📱 Usuario: {data.get('personal_data', {}).get('name', 'No disponible')}")
            print(f"🎨 Perfil: {data.get('profile_summary', 'No disponible')[:100]}...")
            return True
        else:
            print(f"❌ Error en integración: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error en integración: {e}")
        return False

def run_complete_test():
    """Ejecuta todas las pruebas"""
    print("🚀 INICIANDO TEST COMPLETO DEL FLUJO DE EVALUATE")
    print("=" * 60)
    
    results = {}
    
    # Test 1: Salud del backend
    results['backend_health'] = test_backend_health()
    print()
    
    # Test 2: Ruta raíz del backend
    results['backend_root'] = test_backend_root()
    print()
    
    # Test 3: Salud del frontend
    results['frontend_health'] = test_frontend_health()
    print()
    
    # Test 4: API de informes
    results['api_informes'], informe_data = test_api_informe_ia()
    print()
    
    # Test 5: Generación de PDFs
    results['api_pdf'] = test_api_pdf_generation()
    print()
    
    # Test 6: Integración frontend-backend
    results['integration'] = test_frontend_backend_integration()
    print()
    
    # Resumen de resultados
    print("=" * 60)
    print("📊 RESUMEN DE RESULTADOS")
    print("=" * 60)
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    
    for test_name, result in results.items():
        status = "✅ PASÓ" if result else "❌ FALLÓ"
        print(f"{test_name.replace('_', ' ').title()}: {status}")
    
    print()
    print(f"🎯 RESULTADO FINAL: {passed_tests}/{total_tests} pruebas pasaron")
    
    if passed_tests == total_tests:
        print("🎉 ¡TODAS LAS PRUEBAS PASARON! El flujo completo funciona correctamente.")
        return True
    else:
        print("⚠️ Algunas pruebas fallaron. Revisa los errores arriba.")
        return False

if __name__ == "__main__":
    try:
        success = run_complete_test()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⏹️ Test interrumpido por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Error inesperado: {e}")
        sys.exit(1)
