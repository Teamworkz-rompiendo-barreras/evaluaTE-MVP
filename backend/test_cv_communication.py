#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de prueba para verificar la comunicación entre frontend y backend
para el análisis de CV.
"""

import requests
import json
import os
from pathlib import Path

def test_cv_analysis_endpoint():
    """Prueba el endpoint de análisis de CV"""
    
    # URL del backend
    backend_url = "http://localhost:8000"
    endpoint = f"{backend_url}/api/pdf/analyze-cv"
    
    print("🧪 Probando comunicación entre frontend y backend...")
    print(f"📍 Endpoint: {endpoint}")
    
    # Verificar que el backend esté funcionando
    try:
        response = requests.get(f"{backend_url}/")
        if response.status_code == 200:
            print("✅ Backend está funcionando")
        else:
            print("❌ Backend no responde correctamente")
            return False
    except Exception as e:
        print(f"❌ No se puede conectar al backend: {e}")
        return False
    
    # Buscar un archivo PDF de prueba
    test_pdf_path = None
    possible_paths = [
        "test_cv_real.pdf",  # Nuevo PDF con texto real
        "test.pdf",
        "cv_prueba.pdf",
        "../test.pdf"
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            test_pdf_path = path
            break
    
    if not test_pdf_path:
        print("❌ No se encontró archivo PDF de prueba")
        print("   Archivos buscados:", possible_paths)
        return False
    
    print(f"📄 Usando archivo de prueba: {test_pdf_path}")
    
    # Preparar datos de prueba
    test_data = {
        'userId': 'test-user-123',
        'fullName': 'Usuario de Prueba',
        'softSkills': json.dumps([]),
        'jobPreferences': json.dumps({}),
        'completedGames': json.dumps([])
    }
    
    # Preparar archivo
    files = {
        'file': ('test.pdf', open(test_pdf_path, 'rb'), 'application/pdf')
    }
    
    try:
        print("📤 Enviando solicitud de análisis...")
        response = requests.post(endpoint, data=test_data, files=files)
        
        print(f"📥 Respuesta recibida: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Análisis exitoso!")
            print(f"📊 Fortalezas: {len(result.get('strengths', []))}")
            print(f"📊 Debilidades: {len(result.get('weaknesses', []))}")
            print(f"📊 Habilidades: {len(result.get('skills', []))}")
            print(f"📝 Feedback: {result.get('feedback', '')[:100]}...")
            return True
        else:
            print(f"❌ Error en el análisis: {response.status_code}")
            try:
                error_data = response.json()
                print(f"🔍 Detalles del error: {error_data}")
            except:
                print(f"🔍 Respuesta de error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error en la comunicación: {e}")
        return False
    finally:
        files['file'][1].close()

def test_report_generation():
    """Prueba la generación del reporte final"""
    
    backend_url = "http://localhost:8000"
    endpoint = f"{backend_url}/api/informe-ia"
    
    print("\n🧪 Probando generación de reporte final...")
    
    # Datos de prueba para el reporte
    test_report_data = {
        "userId": "test-user-123",
        "fullName": "Usuario de Prueba",
        "softSkills": [
            {
                "skill": "Comunicación",
                "score": 85,
                "level": "alto",
                "confidence": 90
            },
            {
                "skill": "Trabajo en equipo",
                "score": 75,
                "level": "medio",
                "confidence": 85
            }
        ],
        "cvAnalysis": {
            "strengths": ["Experiencia técnica sólida"],
            "weaknesses": ["Falta de experiencia en gestión"],
            "feedback": "CV bien estructurado con buena experiencia técnica",
            "structure": "buena",
            "coherence": "alta",
            "experience": "sólida",
            "skills": ["Python", "JavaScript", "React"],
            "education": ["Ingeniería Informática"],
            "alerts": []
        },
        "jobPreferences": {
            "areas": ["Desarrollo web", "Frontend"],
            "needs": ["Trabajo remoto", "Flexibilidad horaria"],
            "workMode": "remoto",
            "availability": "completa",
            "willingToRelocate": False,
            "hasDisabilityCert": False
        },
        "completedGames": ["1", "2"],
        "logs": []
    }
    
    try:
        print("📤 Enviando solicitud de reporte...")
        response = requests.post(
            endpoint,
            json=test_report_data,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"📥 Respuesta recibida: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Reporte generado exitosamente!")
            print(f"📊 Puntuación: {result.get('employabilityScore', 'N/A')}")
            print(f"📊 Nivel: {result.get('level', 'N/A')}")
            print(f"📝 Resumen: {result.get('summary', '')[:100]}...")
            return True
        else:
            print(f"❌ Error en la generación: {response.status_code}")
            try:
                error_data = response.json()
                print(f"🔍 Detalles del error: {error_data}")
            except:
                print(f"🔍 Respuesta de error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error en la comunicación: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Iniciando pruebas de comunicación...")
    
    # Prueba 1: Análisis de CV
    cv_test_passed = test_cv_analysis_endpoint()
    
    # Prueba 2: Generación de reporte
    report_test_passed = test_report_generation()
    
    # Resumen
    print("\n" + "="*50)
    print("📋 RESUMEN DE PRUEBAS")
    print("="*50)
    print(f"✅ Análisis de CV: {'PASÓ' if cv_test_passed else 'FALLÓ'}")
    print(f"✅ Generación de reporte: {'PASÓ' if report_test_passed else 'FALLÓ'}")
    
    if cv_test_passed and report_test_passed:
        print("\n🎉 ¡Todas las pruebas pasaron! La comunicación está funcionando correctamente.")
    else:
        print("\n⚠️ Algunas pruebas fallaron. Revisa los logs para más detalles.") 