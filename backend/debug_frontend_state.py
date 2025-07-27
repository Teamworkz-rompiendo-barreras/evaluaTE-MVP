#!/usr/bin/env python3
"""
Script para diagnosticar el estado del frontend y verificar por qué no se guardan los datos del CV
"""

import os
import sys
import json
import requests
from pathlib import Path

def test_cv_upload_flow():
    """Prueba el flujo completo de subida de CV para verificar dónde se pierde la información"""
    print("🔍 Probando flujo completo de subida de CV...")
    
    # Buscar un archivo PDF de prueba
    pdf_files = list(Path('.').glob('*.pdf'))
    if not pdf_files:
        print("❌ No se encontraron archivos PDF para probar")
        return False
    
    test_pdf = pdf_files[0]
    print(f"📄 Usando archivo: {test_pdf}")
    
    # Paso 1: Subir CV para análisis
    print("\n📤 Paso 1: Subiendo CV para análisis...")
    upload_url = "http://localhost:8000/api/pdf/analyze-cv"
    
    form_data = {
        'userId': 'user-ester-2025',
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
        with open(test_pdf, 'rb') as f:
            files = {'file': (test_pdf.name, f, 'application/pdf')}
            
            response = requests.post(upload_url, files=files, data=form_data, timeout=60)
        
        if response.status_code == 200:
            cv_analysis = response.json()
            print("✅ CV analizado correctamente")
            print(f"📊 Datos extraídos: {len(cv_analysis)} campos")
            
            # Verificar que se extrajeron datos reales
            if cv_analysis.get('strengths') or cv_analysis.get('weaknesses') or cv_analysis.get('skills'):
                print("✅ Se extrajeron datos reales del CV")
                
                # Mostrar algunos datos extraídos
                if cv_analysis.get('strengths'):
                    print(f"✅ Fortalezas: {len(cv_analysis['strengths'])} elementos")
                if cv_analysis.get('weaknesses'):
                    print(f"✅ Debilidades: {len(cv_analysis['weaknesses'])} elementos")
                if cv_analysis.get('skills'):
                    print(f"✅ Habilidades: {len(cv_analysis['skills'])} elementos")
                
                return cv_analysis
            else:
                print("⚠️ No se extrajeron datos significativos del CV")
                print(f"📊 Resultado: {cv_analysis}")
                return False
        else:
            print(f"❌ Error en análisis de CV: {response.status_code}")
            print(f"Respuesta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

def test_frontend_state_simulation():
    """Simula el estado que debería tener el frontend después de subir el CV"""
    print("\n🔄 Simulando estado del frontend después de subir CV...")
    
    # Obtener análisis real del CV
    cv_analysis = test_cv_upload_flow()
    if not cv_analysis:
        print("❌ No se pudo obtener análisis del CV")
        return False
    
    # Simular el estado que debería tener el frontend
    frontend_state = {
        "userId": "user-ester-2025",
        "fullName": "Esther Pérez",
        "cvAnalysis": cv_analysis,  # Datos reales del CV
        "softSkills": [
            {
                "skill": "Toma de decisiones",
                "score": 40,
                "level": "Bajo",
                "confidence": 40
            }
        ],
        "jobPreferences": {
            "areas": ["grabadora de datos"],
            "needs": ["Necesito flexibilidad horaria"],
            "workMode": "remoto"
        },
        "completedGames": [
            "decision-making", 
            "analytical-thinking", 
            "creativity", 
            "social-influence", 
            "curiosity-learning"
        ],
        "logs": []
    }
    
    print("✅ Estado del frontend simulado correctamente")
    print(f"📊 cvAnalysis tiene {len(cv_analysis)} campos")
    
    return frontend_state

def test_informe_generation_with_real_state():
    """Prueba la generación del informe con el estado real del frontend"""
    print("\n📋 Generando informe con estado real del frontend...")
    
    # Obtener estado simulado del frontend
    frontend_state = test_frontend_state_simulation()
    if not frontend_state:
        print("❌ No se pudo simular el estado del frontend")
        return False
    
    # Generar informe con datos reales
    url = "http://localhost:8000/api/informe-ia"
    
    try:
        response = requests.post(
            url,
            json=frontend_state,
            headers={'Content-Type': 'application/json'},
            timeout=120
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Informe generado correctamente")
            
            if 'report' in result and 'informeProfesional' in result['report']:
                informe = result['report']['informeProfesional']
                print(f"📄 Longitud del informe: {len(informe)} caracteres")
                
                # Verificar que el informe incluya datos del CV
                cv_keywords = []
                if frontend_state['cvAnalysis'].get('strengths'):
                    cv_keywords.extend(frontend_state['cvAnalysis']['strengths'])
                if frontend_state['cvAnalysis'].get('skills'):
                    cv_keywords.extend(frontend_state['cvAnalysis']['skills'])
                
                found_keywords = []
                for keyword in cv_keywords[:5]:  # Solo verificar los primeros 5
                    if keyword in informe:
                        found_keywords.append(keyword)
                
                if found_keywords:
                    print(f"✅ El informe incluye datos del CV: {found_keywords}")
                    return True
                else:
                    print("⚠️ El informe no incluye datos específicos del CV")
                    return False
            else:
                print("❌ No se generó el informe profesional")
                return False
        else:
            print(f"❌ Error generando informe: {response.status_code}")
            print(f"Respuesta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

def compare_frontend_vs_backend():
    """Compara lo que envía el frontend vs lo que debería enviar"""
    print("\n🔍 Comparando frontend vs backend...")
    
    # Lo que está enviando el frontend (según el log)
    frontend_sending = {
        "cvAnalysis": {
            "strengths": [],
            "weaknesses": [],
            "feedback": "No se pudo analizar completamente el CV",
            "structure": "regular",
            "coherence": "regular",
            "experience": "regular",
            "skills": [],
            "education": [],
            "alerts": ["Error en el análisis del CV"]
        }
    }
    
    # Lo que debería enviar (datos reales)
    real_cv_analysis = test_cv_upload_flow()
    if real_cv_analysis:
        backend_should_send = {
            "cvAnalysis": real_cv_analysis
        }
        
        print("📊 COMPARACIÓN:")
        print(f"Frontend envía: {len(frontend_sending['cvAnalysis']['strengths'])} fortalezas")
        print(f"Backend debería: {len(backend_should_send['cvAnalysis']['strengths'])} fortalezas")
        print(f"Frontend envía: {len(frontend_sending['cvAnalysis']['skills'])} habilidades")
        print(f"Backend debería: {len(backend_should_send['cvAnalysis']['skills'])} habilidades")
        
        return True
    else:
        print("❌ No se pudo obtener análisis real del CV")
        return False

def main():
    """Función principal"""
    print("🧪 Iniciando diagnóstico del estado del frontend...")
    print("=" * 70)
    
    tests = [
        ("Flujo de Subida de CV", test_cv_upload_flow),
        ("Estado del Frontend", test_frontend_state_simulation),
        ("Generación de Informe", test_informe_generation_with_real_state),
        ("Comparación Frontend vs Backend", compare_frontend_vs_backend)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*25} {test_name} {'='*25}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Error inesperado en {test_name}: {e}")
            results.append((test_name, False))
    
    # Resumen
    print(f"\n{'='*70}")
    print("📊 RESUMEN DEL DIAGNÓSTICO")
    print("=" * 70)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASÓ" if result else "❌ FALLÓ"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nResultado: {passed}/{len(results)} pruebas pasaron")
    
    if passed == len(results):
        print("🎉 El problema está identificado: el frontend no está guardando el análisis del CV")
        print("💡 Solución: Verificar que saveCvAnalysis se ejecute correctamente en UploadCVPage.tsx")
    else:
        print("⚠️ Se identificaron problemas. Revisa los errores anteriores.")
    
    return passed == len(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 