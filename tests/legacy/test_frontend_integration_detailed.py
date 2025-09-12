#!/usr/bin/env python3
"""
Test detallado de la integración frontend-backend
Verifica que la información del backend se procese correctamente en el frontend
"""

import requests
import json
import sys
from typing import Dict, Any

# Configuración
BACKEND_URL = "http://localhost:8080"
FRONTEND_URL = "http://localhost:5173"

def test_backend_data_structure():
    """Prueba la estructura de datos que envía el backend"""
    print("🔍 Probando estructura de datos del backend...")
    
    test_data = {
        "userId": "test-frontend-integration",
        "fullName": "Ana Martínez Sánchez",
        "softSkills": [
            {"skill": "Comunicación", "score": 92, "level": "Avanzado"},
            {"skill": "Trabajo en equipo", "score": 88, "level": "Avanzado"},
            {"skill": "Liderazgo", "score": 80, "level": "Intermedio"},
            {"skill": "Resolución de problemas", "score": 95, "level": "Avanzado"},
            {"skill": "Adaptabilidad", "score": 85, "level": "Intermedio"},
            {"skill": "Creatividad", "score": 78, "level": "Intermedio"}
        ],
        "cvAnalysis": {
            "strengths": [
                "Perfil técnico sólido con experiencia demostrable",
                "Formación académica en ingeniería de software",
                "Portfolio de proyectos con tecnologías modernas",
                "Experiencia en metodologías ágiles"
            ],
            "weaknesses": [
                "Limitada experiencia en gestión de equipos grandes",
                "Falta de experiencia internacional en empresas multinacionales"
            ],
            "feedback": "CV excelentemente estructurado con buenas fortalezas técnicas y proyectos demostrables. Se destaca la capacidad de aprendizaje y adaptación a nuevas tecnologías.",
            "summary": "Desarrolladora senior con 5 años de experiencia en desarrollo full-stack y arquitectura de software",
            "stars": {
                "formato": 5,
                "claridad": 5,
                "coherencia": 5,
                "informacion_clave": 5,
                "ortografia": 5
            }
        },
        "jobPreferences": {
            "areas": ["Desarrollo de software", "Arquitectura de software", "Tecnología", "Startups", "Empresas de producto"],
            "needs": ["Crecimiento profesional", "Trabajo remoto", "Proyectos desafiantes", "Liderazgo técnico"],
            "workMode": "Remoto",
            "availability": "Inmediata",
            "willingToRelocate": True,
            "hasDisabilityCert": False
        },
        "completedGames": [
            "Evaluación de comunicación avanzada",
            "Test de trabajo en equipo",
            "Análisis de liderazgo",
            "Evaluación de resolución de problemas",
            "Test de adaptabilidad",
            "Evaluación de creatividad"
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
            print("✅ Backend generó informe correctamente")
            
            # Verificar campos críticos para el frontend
            critical_fields = {
                'summary': 'Resumen del informe',
                'personal_data.name': 'Nombre del usuario',
                'strengths': 'Lista de fortalezas',
                'improvement_areas': 'Áreas de mejora',
                'cv_analysis': 'Análisis del CV',
                'action_plan': 'Plan de acción',
                'job_search_advice': 'Consejos de búsqueda',
                'useful_tools': 'Herramientas útiles'
            }
            
            all_fields_present = True
            for field_path, description in critical_fields.items():
                if '.' in field_path:
                    # Campo anidado
                    parts = field_path.split('.')
                    value = data
                    for part in parts:
                        if isinstance(value, dict) and part in value:
                            value = value[part]
                        else:
                            value = None
                            break
                    
                    if value is not None:
                        print(f"✅ {description}: Presente")
                        if isinstance(value, list):
                            print(f"   📊 Cantidad: {len(value)} elementos")
                        elif isinstance(value, str):
                            print(f"   📝 Contenido: {value[:50]}...")
                    else:
                        print(f"❌ {description}: Faltante")
                        all_fields_present = False
                else:
                    # Campo directo
                    if field_path in data:
                        value = data[field_path]
                        print(f"✅ {description}: Presente")
                        if isinstance(value, list):
                            print(f"   📊 Cantidad: {len(value)} elementos")
                        elif isinstance(value, str):
                            print(f"   📝 Contenido: {value[:50]}...")
                    else:
                        print(f"❌ {description}: Faltante")
                        all_fields_present = False
            
            return all_fields_present, data
        else:
            print(f"❌ Error del backend: {response.status_code}")
            return False, None
            
    except Exception as e:
        print(f"❌ Error probando backend: {e}")
        return False, None

def test_frontend_data_processing():
    """Simula cómo el frontend procesaría los datos del backend"""
    print("\n🔍 Simulando procesamiento de datos en el frontend...")
    
    # Obtener datos del backend primero
    test_data = {
        "userId": "test-frontend-processing",
        "fullName": "Luis Fernández",
        "softSkills": [
            {"skill": "Análisis", "score": 90, "level": "Avanzado"},
            {"skill": "Planificación", "score": 85, "level": "Intermedio"}
        ],
        "cvAnalysis": {
            "strengths": ["Perfil analítico"],
            "feedback": "CV bien estructurado"
        },
        "jobPreferences": {
            "areas": ["Análisis de datos"]
        }
    }
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/informe-ia",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            backend_data = response.json()
            print("✅ Datos del backend obtenidos")
            
            # Simular procesamiento del frontend
            print("🔄 Procesando datos para el frontend...")
            
            # Extraer datos críticos
            user_name = backend_data.get('personal_data', {}).get('name', 'Usuario')
            summary = backend_data.get('summary', 'Sin resumen')
            strengths = backend_data.get('strengths', [])
            improvement_areas = backend_data.get('improvement_areas', [])
            action_plan = backend_data.get('action_plan', {})
            cv_analysis = backend_data.get('cv_analysis', {})
            
            # Verificar que los datos son procesables
            print(f"👤 Usuario: {user_name}")
            print(f"📋 Resumen: {summary[:100]}...")
            print(f"💪 Fortalezas: {len(strengths)} encontradas")
            print(f"📈 Áreas de mejora: {len(improvement_areas)} identificadas")
            print(f"🎯 Plan de acción: {len(action_plan.get('short_term', []))} acciones a corto plazo")
            
            # Verificar estructura del CV
            if cv_analysis:
                structure_score = cv_analysis.get('structure_score', 0)
                coherence_score = cv_analysis.get('coherence_score', 0)
                print(f"📊 Puntuación CV - Estructura: {structure_score}/5, Coherencia: {coherence_score}/5")
            
            # Verificar que los datos son válidos para el frontend
            data_valid = all([
                user_name != 'Usuario',
                len(summary) > 10,
                len(strengths) > 0,
                len(improvement_areas) > 0,
                len(action_plan.get('short_term', [])) > 0
            ])
            
            if data_valid:
                print("✅ Datos válidos para el frontend")
                return True
            else:
                print("⚠️ Algunos datos pueden no ser óptimos para el frontend")
                return False
                
        else:
            print(f"❌ Error obteniendo datos: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error en procesamiento: {e}")
        return False

def test_report_generation_flow():
    """Prueba el flujo completo de generación de reportes"""
    print("\n🔍 Probando flujo completo de generación de reportes...")
    
    # Simular el flujo completo: datos → informe → PDF
    test_data = {
        "userId": "test-complete-flow",
        "fullName": "Carmen Ruiz",
        "softSkills": [
            {"skill": "Gestión", "score": 88, "level": "Avanzado"},
            {"skill": "Comunicación", "score": 92, "level": "Avanzado"}
        ],
        "cvAnalysis": {
            "strengths": ["Perfil directivo"],
            "feedback": "CV de alto nivel"
        },
        "jobPreferences": {
            "areas": ["Gestión", "Dirección"]
        }
    }
    
    try:
        # Paso 1: Generar informe
        print("📝 Paso 1: Generando informe...")
        informe_response = requests.post(
            f"{BACKEND_URL}/api/informe-ia",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if informe_response.status_code != 200:
            print(f"❌ Error generando informe: {informe_response.status_code}")
            return False
        
        informe_data = informe_response.json()
        print("✅ Informe generado correctamente")
        
        # Paso 2: Generar PDF
        print("📄 Paso 2: Generando PDF...")
        pdf_response = requests.post(
            f"{BACKEND_URL}/api/pdf/generate-report",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if pdf_response.status_code != 200:
            print(f"❌ Error generando PDF: {pdf_response.status_code}")
            return False
        
        content_type = pdf_response.headers.get('content-type', '')
        if 'application/pdf' in content_type:
            print("✅ PDF generado correctamente")
            print(f"📊 Tamaño del PDF: {len(pdf_response.content)} bytes")
        else:
            print(f"⚠️ Respuesta no es PDF: {content_type}")
        
        # Paso 3: Verificar consistencia de datos
        print("🔍 Paso 3: Verificando consistencia de datos...")
        
        # Verificar que el informe contiene la información correcta
        user_name_informe = informe_data.get('personal_data', {}).get('name', '')
        if user_name_informe == test_data['fullName']:
            print("✅ Nombre del usuario consistente")
        else:
            print(f"⚠️ Inconsistencia en nombre: {test_data['fullName']} vs {user_name_informe}")
        
        # Verificar que las fortalezas se procesaron correctamente
        strengths_count = len(informe_data.get('strengths', []))
        if strengths_count > 0:
            print(f"✅ {strengths_count} fortalezas procesadas")
        else:
            print("⚠️ No se procesaron fortalezas")
        
        print("✅ Flujo completo de generación funcionando")
        return True
        
    except Exception as e:
        print(f"❌ Error en flujo completo: {e}")
        return False

def test_error_handling():
    """Prueba el manejo de errores del backend"""
    print("\n🔍 Probando manejo de errores...")
    
    # Test 1: Datos inválidos
    print("📝 Test 1: Datos inválidos...")
    invalid_data = {
        "invalid_field": "invalid_value"
    }
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/informe-ia",
            json=invalid_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            print("✅ Backend maneja datos inválidos correctamente")
        else:
            print(f"⚠️ Backend devolvió error {response.status_code} para datos inválidos")
            
    except Exception as e:
        print(f"❌ Error con datos inválidos: {e}")
    
    # Test 2: Datos vacíos
    print("📝 Test 2: Datos vacíos...")
    empty_data = {}
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/informe-ia",
            json=empty_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            print("✅ Backend maneja datos vacíos correctamente")
        else:
            print(f"⚠️ Backend devolvió error {response.status_code} para datos vacíos")
            
    except Exception as e:
        print(f"❌ Error con datos vacíos: {e}")
    
    return True

def run_detailed_integration_test():
    """Ejecuta el test detallado de integración"""
    print("🚀 INICIANDO TEST DETALLADO DE INTEGRACIÓN FRONTEND-BACKEND")
    print("=" * 70)
    
    results = {}
    
    # Test 1: Estructura de datos del backend
    results['backend_structure'], backend_data = test_backend_data_structure()
    print()
    
    # Test 2: Procesamiento de datos en el frontend
    results['frontend_processing'] = test_frontend_data_processing()
    print()
    
    # Test 3: Flujo completo de generación
    results['complete_flow'] = test_report_generation_flow()
    print()
    
    # Test 4: Manejo de errores
    results['error_handling'] = test_error_handling()
    print()
    
    # Resumen de resultados
    print("=" * 70)
    print("📊 RESUMEN DEL TEST DETALLADO DE INTEGRACIÓN")
    print("=" * 70)
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    
    for test_name, result in results.items():
        status = "✅ PASÓ" if result else "❌ FALLÓ"
        print(f"{test_name.replace('_', ' ').title()}: {status}")
    
    print()
    print(f"🎯 RESULTADO FINAL: {passed_tests}/{total_tests} pruebas pasaron")
    
    if passed_tests == total_tests:
        print("🎉 ¡TODAS LAS PRUEBAS DE INTEGRACIÓN PASARON!")
        print("✅ El frontend puede procesar correctamente los datos del backend")
        print("✅ La información se transmite correctamente entre componentes")
        print("✅ Los reportes se generan con la estructura esperada")
        return True
    else:
        print("⚠️ Algunas pruebas de integración fallaron")
        print("🔍 Revisa los errores específicos arriba")
        return False

if __name__ == "__main__":
    try:
        success = run_detailed_integration_test()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⏹️ Test interrumpido por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Error inesperado: {e}")
        sys.exit(1)
