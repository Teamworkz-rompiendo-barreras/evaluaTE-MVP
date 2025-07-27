#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para verificar si el problema está en el frontend o en cómo se está mostrando el informe.
"""

import requests
import json
import os

def verificar_informe_frontend():
    """Verifica si el problema está en el frontend"""
    
    print("🔍 VERIFICACIÓN: Problema en Frontend vs Backend")
    print("=" * 60)
    
    # Configuración
    base_url = "http://localhost:8000"
    cv_file_path = "cv_prueba.pdf"
    
    # Verificar que el archivo existe
    if not os.path.exists(cv_file_path):
        print(f"❌ Error: No se encuentra el archivo {cv_file_path}")
        return False
    
    print(f"📄 Archivo CV: {cv_file_path}")
    
    # Paso 1: Analizar el CV
    print("\n📋 PASO 1: Analizando CV...")
    
    cv_analysis_data = {
        "userId": "frontend_test",
        "fullName": "Test Frontend",
        "softSkills": json.dumps([
            {
                "skill": "Comunicación",
                "score": 78,
                "level": "medio",
                "confidence": 85
            },
            {
                "skill": "Trabajo en equipo",
                "score": 82,
                "level": "alto",
                "confidence": 88
            }
        ]),
        "jobPreferences": json.dumps({
            "areas": ["Desarrollo web", "Diseño gráfico"],
            "needs": ["Flexibilidad horaria", "Trabajo remoto"],
            "workMode": "remoto",
            "availability": "completa",
            "willingToRelocate": False,
            "hasDisabilityCert": False
        }),
        "completedGames": json.dumps(["comunicacion_equipo", "resolucion_problemas"])
    }
    
    try:
        # Analizar CV
        with open(cv_file_path, 'rb') as f:
            files = {'file': (cv_file_path, f, 'application/pdf')}
            
            response = requests.post(
                f"{base_url}/api/pdf/analyze-cv",
                files=files,
                data=cv_analysis_data,
                timeout=60
            )
        
        if response.status_code != 200:
            print(f"❌ Error analizando CV: {response.status_code}")
            print(f"Detalle: {response.text}")
            return False
        
        cv_analysis = response.json()
        print("✅ CV analizado exitosamente")
        
    except Exception as e:
        print(f"❌ Error en análisis de CV: {str(e)}")
        return False
    
    # Paso 2: Generar informe completo
    print("\n📋 PASO 2: Generando informe completo...")
    
    # Datos completos para el informe
    complete_report_data = {
        "userId": "frontend_test",
        "fullName": "Test Frontend",
        "softSkills": [
            {
                "skill": "Comunicación",
                "score": 78,
                "level": "medio",
                "confidence": 85
            },
            {
                "skill": "Trabajo en equipo",
                "score": 82,
                "level": "alto",
                "confidence": 88
            }
        ],
        "cvAnalysis": cv_analysis,  # Usar el análisis real del CV
        "jobPreferences": {
            "areas": ["Desarrollo web", "Diseño gráfico"],
            "needs": ["Flexibilidad horaria", "Trabajo remoto"],
            "workMode": "remoto",
            "availability": "completa",
            "willingToRelocate": False,
            "hasDisabilityCert": False
        },
        "completedGames": ["comunicacion_equipo", "resolucion_problemas"],
        "logs": [
            {
                "sceneId": 1,
                "decisions": [
                    {"decision": "Escuchar activamente", "confidence": 85, "time": 3000},
                    {"decision": "Proponer solución", "confidence": 78, "time": 4500}
                ],
                "totalSteps": 2,
                "totalTime": 7500,
                "averageConfidence": 81.5,
                "emotionalTrend": ["confiado", "colaborativo"],
                "accessibilityUsed": False
            }
        ]
    }
    
    try:
        # Generar informe completo
        response = requests.post(
            f"{base_url}/api/logs/report",
            json=complete_report_data,
            timeout=120
        )
        
        if response.status_code != 200:
            print(f"❌ Error generando informe: {response.status_code}")
            print(f"Detalle: {response.text}")
            return False
        
        report = response.json()
        print("✅ Informe completo generado exitosamente")
        
        # Analizar la respuesta completa
        print(f"\n📊 ANÁLISIS DE LA RESPUESTA:")
        print(f"  • Código de respuesta: {response.status_code}")
        print(f"  • Tamaño de respuesta: {len(response.content)} bytes")
        
        # Verificar estructura de la respuesta
        report_content = report.get('report', {})
        
        print(f"\n📋 ESTRUCTURA DE LA RESPUESTA:")
        print(f"  • Claves principales: {list(report.keys())}")
        print(f"  • Claves del report: {list(report_content.keys())}")
        
        # Verificar datos específicos
        print(f"\n📊 DATOS ESPECÍFICOS:")
        print(f"  • employabilityScore: {report.get('employabilityScore')}")
        print(f"  • level: {report.get('level')}")
        print(f"  • summary: {report.get('summary')}")
        
        # Verificar CV en la respuesta
        cv_in_report = report_content.get('cvAnalysis')
        print(f"\n📄 ANÁLISIS DEL CV EN LA RESPUESTA:")
        print(f"  • CV presente: {'✅ SÍ' if cv_in_report else '❌ NO'}")
        
        if cv_in_report:
            print(f"  • Fortalezas: {len(cv_in_report.get('strengths', []))}")
            print(f"  • Habilidades: {len(cv_in_report.get('skills', []))}")
            print(f"  • Formación: {len(cv_in_report.get('education', []))}")
        
        # Verificar informe profesional
        informe_profesional = report_content.get('informeProfesional', '')
        print(f"\n📝 INFORME PROFESIONAL:")
        print(f"  • Presente: {'✅ SÍ' if informe_profesional else '❌ NO'}")
        print(f"  • Longitud: {len(informe_profesional)} caracteres")
        
        if informe_profesional:
            # Buscar secciones específicas del CV
            cv_sections = [
                "análisis crítico del cv" in informe_profesional.lower(),
                "evaluación comprehensiva de experiencia" in informe_profesional.lower(),
                "cv de" in informe_profesional.lower(),
                "estructura del cv" in informe_profesional.lower(),
                "habilidades técnicas" in informe_profesional.lower()
            ]
            
            print(f"  • Secciones de CV encontradas: {sum(cv_sections)} de 5")
            
            # Mostrar líneas que contengan "CV"
            cv_lines = [line for line in informe_profesional.split('\n') if 'cv' in line.lower()]
            print(f"  • Líneas con 'CV': {len(cv_lines)}")
            
            if cv_lines:
                print(f"\n📋 LÍNEAS CON 'CV':")
                for i, line in enumerate(cv_lines[:5], 1):
                    print(f"  {i}. {line.strip()}")
        
        # Guardar respuesta completa para análisis
        with open("RESPUESTA_COMPLETA_FRONTEND.json", 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Respuesta completa guardada en: RESPUESTA_COMPLETA_FRONTEND.json")
        
        return True
        
    except Exception as e:
        print(f"❌ Error generando informe: {str(e)}")
        return False

def verificar_endpoint_directo():
    """Verifica el endpoint directamente sin CV para comparar"""
    
    print("\n" + "="*60)
    print("🔍 VERIFICACIÓN: Endpoint sin CV")
    print("=" * 60)
    
    base_url = "http://localhost:8000"
    
    # Datos sin CV
    report_data_sin_cv = {
        "userId": "test_sin_cv",
        "fullName": "Test Sin CV",
        "softSkills": [
            {
                "skill": "Comunicación",
                "score": 78,
                "level": "medio",
                "confidence": 85
            },
            {
                "skill": "Trabajo en equipo",
                "score": 82,
                "level": "alto",
                "confidence": 88
            }
        ],
        "cvAnalysis": None,  # Sin CV
        "jobPreferences": {
            "areas": ["Desarrollo web", "Diseño gráfico"],
            "needs": ["Flexibilidad horaria", "Trabajo remoto"],
            "workMode": "remoto",
            "availability": "completa",
            "willingToRelocate": False,
            "hasDisabilityCert": False
        },
        "completedGames": ["comunicacion_equipo", "resolucion_problemas"],
        "logs": [
            {
                "sceneId": 1,
                "decisions": [
                    {"decision": "Escuchar activamente", "confidence": 85, "time": 3000}
                ],
                "totalSteps": 1,
                "totalTime": 3000,
                "averageConfidence": 85,
                "emotionalTrend": ["confiado"],
                "accessibilityUsed": False
            }
        ]
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/logs/report",
            json=report_data_sin_cv,
            timeout=120
        )
        
        if response.status_code != 200:
            print(f"❌ Error: {response.status_code}")
            return False
        
        report_sin_cv = response.json()
        informe_sin_cv = report_sin_cv.get('report', {}).get('informeProfesional', '')
        
        print(f"✅ Informe sin CV generado")
        print(f"📏 Longitud: {len(informe_sin_cv)} caracteres")
        
        # Comparar con el informe con CV
        with open("DEBUG_INFORME_COMPLETO.txt", 'r', encoding='utf-8') as f:
            informe_con_cv = f.read()
        
        print(f"\n📊 COMPARACIÓN:")
        print(f"  • Informe con CV: {len(informe_con_cv)} caracteres")
        print(f"  • Informe sin CV: {len(informe_sin_cv)} caracteres")
        print(f"  • Diferencia: {len(informe_con_cv) - len(informe_sin_cv)} caracteres")
        
        # Buscar menciones de CV
        cv_mentions_con = informe_con_cv.lower().count('cv')
        cv_mentions_sin = informe_sin_cv.lower().count('cv')
        
        print(f"  • Menciones 'CV' con CV: {cv_mentions_con}")
        print(f"  • Menciones 'CV' sin CV: {cv_mentions_sin}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 VERIFICACIÓN COMPLETA: Frontend vs Backend")
    print("=" * 60)
    
    # Verificación 1: Informe con CV
    test1_success = verificar_informe_frontend()
    
    # Verificación 2: Comparación sin CV
    test2_success = verificar_endpoint_directo()
    
    print("\n" + "="*60)
    print("📊 RESUMEN DE VERIFICACIÓN")
    print("="*60)
    print(f"✅ Verificación con CV: {'EXITOSO' if test1_success else 'FALLIDO'}")
    print(f"✅ Comparación sin CV: {'EXITOSO' if test2_success else 'FALLIDO'}")
    
    if test1_success and test2_success:
        print("\n🎉 ¡VERIFICACIÓN COMPLETADA!")
        print("El backend está funcionando correctamente.")
        print("El problema debe estar en el frontend o en la visualización.")
    else:
        print("\n⚠️ Algunas verificaciones fallaron.") 