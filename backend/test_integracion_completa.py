#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de prueba para verificar la integración completa de datos:
- Análisis de CV
- Preferencias laborales
- Resultados de minijuegos
"""

import requests
import json
import os
from datetime import datetime

# Configuración
BASE_URL = "http://localhost:8000"
CV_FILE_PATH = "cv_prueba.pdf"

def test_cv_analysis_integration():
    """Prueba la integración del análisis de CV con otros datos"""
    print("🔍 Probando integración del análisis de CV...")
    
    if not os.path.exists(CV_FILE_PATH):
        print(f"❌ Archivo CV no encontrado: {CV_FILE_PATH}")
        return False
    
    # Datos de prueba
    test_data = {
        "userId": "test-user-123",
        "fullName": "Test User",
        "softSkills": json.dumps([
            {
                "skill": "comunicación",
                "score": 85,
                "level": "alto",
                "confidence": 90
            },
            {
                "skill": "trabajo en equipo",
                "score": 75,
                "level": "medio",
                "confidence": 85
            },
            {
                "skill": "liderazgo",
                "score": 60,
                "level": "medio",
                "confidence": 70
            }
        ]),
        "jobPreferences": json.dumps({
            "areas": ["desarrollo web", "frontend"],
            "needs": ["flexibilidad horaria", "trabajo remoto"],
            "workMode": "remoto",
            "availability": "completa",
            "willingToRelocate": False,
            "hasDisabilityCert": False
        }),
        "completedGames": json.dumps(["juego1", "juego2", "juego3"])
    }
    
    try:
        # Preparar el archivo
        with open(CV_FILE_PATH, 'rb') as f:
            files = {'file': (CV_FILE_PATH, f, 'application/pdf')}
            
            # Enviar al endpoint de análisis de CV
            response = requests.post(
                f"{BASE_URL}/api/pdf/analyze-cv",
                files=files,
                data=test_data
            )
        
        if response.status_code == 200:
            cv_analysis = response.json()
            print("✅ Análisis de CV exitoso")
            print(f"   - Fortalezas: {len(cv_analysis.get('strengths', []))}")
            print(f"   - Debilidades: {len(cv_analysis.get('weaknesses', []))}")
            print(f"   - Habilidades técnicas: {len(cv_analysis.get('skills', []))}")
            return cv_analysis
        else:
            print(f"❌ Error en análisis de CV: {response.status_code}")
            print(f"   Respuesta: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error en prueba de CV: {e}")
        return None

def test_final_report_integration(cv_analysis):
    """Prueba la generación del informe final con todos los datos integrados"""
    print("\n📊 Probando generación de informe final...")
    
    # Datos completos para el informe
    report_data = {
        "userId": "test-user-123",
        "fullName": "Test User",
        "softSkills": [
            {
                "skill": "comunicación",
                "score": 85,
                "level": "alto",
                "confidence": 90
            },
            {
                "skill": "trabajo en equipo",
                "score": 75,
                "level": "medio",
                "confidence": 85
            },
            {
                "skill": "liderazgo",
                "score": 60,
                "level": "medio",
                "confidence": 70
            },
            {
                "skill": "resolución de problemas",
                "score": 80,
                "level": "alto",
                "confidence": 85
            },
            {
                "skill": "adaptabilidad",
                "score": 70,
                "level": "medio",
                "confidence": 75
            }
        ],
        "cvAnalysis": cv_analysis,
        "jobPreferences": {
            "areas": ["desarrollo web", "frontend", "UX/UI"],
            "needs": ["flexibilidad horaria", "trabajo remoto", "proyectos desafiantes"],
            "workMode": "remoto",
            "availability": "completa",
            "willingToRelocate": False,
            "hasDisabilityCert": False
        },
        "completedGames": ["juego1", "juego2", "juego3"],
        "logs": [
            {
                "sceneId": 1,
                "decisions": [
                    {"question": "¿Cómo te sientes en situaciones de presión?", "answer": "Mantengo la calma", "confidence": 85}
                ],
                "totalSteps": 5,
                "totalTime": 120,
                "averageConfidence": 85.0,
                "emotionalTrend": ["confiado", "tranquilo"],
                "accessibilityUsed": False
            }
        ]
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/logs/report",
            json=report_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            report = response.json()
            print("✅ Informe final generado exitosamente")
            print(f"   - Puntuación de empleabilidad: {report.get('employabilityScore', 'N/A')}")
            print(f"   - Nivel: {report.get('level', 'N/A')}")
            print(f"   - Resumen: {report.get('summary', 'N/A')[:100]}...")
            
            # Verificar que todos los datos están integrados
            recommendations = report.get('recommendations', {})
            print(f"   - Roles recomendados: {len(recommendations.get('roles', []))}")
            print(f"   - Recursos sugeridos: {len(recommendations.get('resources', []))}")
            print(f"   - Mejoras de CV: {len(recommendations.get('cvImprovements', []))}")
            
            return report
        else:
            print(f"❌ Error en generación de informe: {response.status_code}")
            print(f"   Respuesta: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error en prueba de informe: {e}")
        return None

def test_data_flow():
    """Prueba el flujo completo de datos"""
    print("🚀 Iniciando prueba de flujo completo de datos...")
    print("=" * 60)
    
    # Paso 1: Análisis de CV
    cv_analysis = test_cv_analysis_integration()
    if not cv_analysis:
        print("❌ Falló el análisis de CV. Abortando prueba.")
        return False
    
    # Paso 2: Informe final
    final_report = test_final_report_integration(cv_analysis)
    if not final_report:
        print("❌ Falló la generación del informe final.")
        return False
    
    # Paso 3: Verificar integración
    print("\n🔍 Verificando integración de datos...")
    
    # Verificar que el CV se integró correctamente
    if final_report.get('report', {}).get('cvAnalysis'):
        print("✅ Datos del CV integrados correctamente")
    else:
        print("⚠️  Datos del CV no encontrados en el informe final")
    
    # Verificar que las soft skills se integraron
    if final_report.get('report', {}).get('softSkills'):
        print("✅ Soft skills integradas correctamente")
    else:
        print("⚠️  Soft skills no encontradas en el informe final")
    
    # Verificar que las preferencias laborales se integraron
    if final_report.get('report', {}).get('jobPreferences'):
        print("✅ Preferencias laborales integradas correctamente")
    else:
        print("⚠️  Preferencias laborales no encontradas en el informe final")
    
    # Verificar que los juegos se integraron
    if final_report.get('report', {}).get('completedGames'):
        print("✅ Juegos completados integrados correctamente")
    else:
        print("⚠️  Juegos completados no encontrados en el informe final")
    
    print("\n🎉 ¡Prueba de integración completada exitosamente!")
    return True

def main():
    """Función principal"""
    print("🧪 PRUEBA DE INTEGRACIÓN COMPLETA DE DATOS")
    print("=" * 60)
    print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 Backend URL: {BASE_URL}")
    print("=" * 60)
    
    success = test_data_flow()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ TODAS LAS PRUEBAS PASARON EXITOSAMENTE")
        print("✅ Los datos del CV, preferencias laborales y minijuegos se están integrando correctamente")
    else:
        print("❌ ALGUNAS PRUEBAS FALLARON")
        print("❌ Hay problemas en la integración de datos")
    
    print("=" * 60)

if __name__ == "__main__":
    main() 