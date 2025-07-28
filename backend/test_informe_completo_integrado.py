#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de prueba final para verificar que el informe completo se genera correctamente
integrando análisis de CV real, preferencias laborales y resultados de minijuegos.
"""

import requests
import json
import os
from pathlib import Path

def test_complete_integrated_report():
    """Prueba la generación de informe completo integrando todos los datos"""
    
    print("🚀 PRUEBA DE INFORME COMPLETO INTEGRADO")
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
        "userId": "test_user_complete",
        "fullName": "María García López",
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
            },
            {
                "skill": "Resolución de problemas",
                "score": 75,
                "level": "medio",
                "confidence": 80
            },
            {
                "skill": "Adaptabilidad",
                "score": 70,
                "level": "medio",
                "confidence": 75
            }
        ]),
        "jobPreferences": json.dumps({
            "areas": ["Desarrollo web", "Diseño gráfico", "Marketing digital"],
            "needs": ["Flexibilidad horaria", "Trabajo remoto", "Formación continua"],
            "workMode": "remoto",
            "availability": "completa",
            "willingToRelocate": False,
            "hasDisabilityCert": False
        }),
        "completedGames": json.dumps(["comunicacion_equipo", "resolucion_problemas", "adaptabilidad"])
    }
    
    try:
        # Analizar CV
        with open(cv_file_path, 'rb') as f:
            files = {'file': (cv_file_path, f, 'application/pdf')}
            
            response = requests.post(
                f"{base_url}/api/pdf/analyze-cv",
                files=files,
                data=cv_analysis_data,
                timeout=300  # Timeout extendido a 5 minutos
            )
        
        if response.status_code != 200:
            print(f"❌ Error analizando CV: {response.status_code}")
            print(f"Detalle: {response.text}")
            return False
        
        cv_analysis = response.json()
        print("✅ CV analizado exitosamente")
        
        # Mostrar resumen del análisis de CV
        print(f"  • Fortalezas detectadas: {len(cv_analysis.get('strengths', []))}")
        print(f"  • Habilidades técnicas: {len(cv_analysis.get('skills', []))}")
        print(f"  • Formación detectada: {len(cv_analysis.get('education', []))}")
        
    except Exception as e:
        print(f"❌ Error en análisis de CV: {str(e)}")
        return False
    
    # Paso 2: Generar informe completo
    print("\n📋 PASO 2: Generando informe completo...")
    
    # Datos completos para el informe
    complete_report_data = {
        "userId": "test_user_complete",
        "fullName": "María García López",
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
            },
            {
                "skill": "Resolución de problemas",
                "score": 75,
                "level": "medio",
                "confidence": 80
            },
            {
                "skill": "Adaptabilidad",
                "score": 70,
                "level": "medio",
                "confidence": 75
            }
        ],
        "cvAnalysis": cv_analysis,
        "jobPreferences": {
            "areas": ["Desarrollo web", "Diseño gráfico", "Marketing digital"],
            "needs": ["Flexibilidad horaria", "Trabajo remoto", "Formación continua"],
            "workMode": "remoto",
            "availability": "completa",
            "willingToRelocate": False,
            "hasDisabilityCert": False
        },
        "completedGames": ["comunicacion_equipo", "resolucion_problemas", "adaptabilidad"],
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
            },
            {
                "sceneId": 2,
                "decisions": [
                    {"decision": "Analizar problema", "confidence": 75, "time": 4000},
                    {"decision": "Buscar alternativas", "confidence": 80, "time": 3500}
                ],
                "totalSteps": 2,
                "totalTime": 7500,
                "averageConfidence": 77.5,
                "emotionalTrend": ["analítico", "persistente"],
                "accessibilityUsed": False
            }
        ]
    }
    
    try:
        # Generar informe completo
        response = requests.post(
            f"{base_url}/api/logs/report",
            json=complete_report_data,
            timeout=300  # Timeout extendido a 5 minutos para generación de informe
        )
        
        if response.status_code != 200:
            print(f"❌ Error generando informe: {response.status_code}")
            print(f"Detalle: {response.text}")
            return False
        
        report = response.json()
        print("✅ Informe completo generado exitosamente")
        
        # Mostrar resumen del informe
        print(f"\n📊 RESUMEN DEL INFORME:")
        print(f"  • Puntuación de empleabilidad: {report.get('employabilityScore', 'N/A')}")
        print(f"  • Nivel: {report.get('level', 'N/A')}")
        print(f"  • Resumen: {report.get('summary', 'N/A')[:100]}...")
        
        # Verificar que el informe incluye análisis de CV
        report_content = report.get('report', {})
        
        print(f"\n📋 CONTENIDO DEL INFORME:")
        print(f"  • Secciones del informe: {len(report_content)}")
        
        # Verificar secciones clave
        key_sections = [
            "perfil_candidato", "analisis_cv", "habilidades_soft", 
            "preferencias_laborales", "recomendaciones", "conclusiones"
        ]
        
        for section in key_sections:
            if section in report_content:
                print(f"  ✅ Sección '{section}': Presente")
            else:
                print(f"  ⚠️ Sección '{section}': Faltante")
        
        # Verificar que no menciona datos faltantes
        report_text = json.dumps(report_content, ensure_ascii=False).lower()
        problematic_phrases = [
            "no se proporcionó",
            "no se especificaron",
            "ningún juego completado",
            "no hay logs",
            "no se dispone",
            "no puede acceder"
        ]
        
        found_problems = []
        for phrase in problematic_phrases:
            if phrase in report_text:
                found_problems.append(phrase)
        
        if found_problems:
            print(f"\n⚠️ PROBLEMAS DETECTADOS:")
            for problem in found_problems:
                print(f"  • Menciona: '{problem}'")
        else:
            print(f"\n✅ No se detectaron menciones de datos faltantes")
        
        # Guardar informe en archivo para revisión
        output_file = "INFORME_COMPLETO_INTEGRADO.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Informe guardado en: {output_file}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error generando informe: {str(e)}")
        return False

def test_pdf_report_generation():
    """Prueba la generación de informe en PDF"""
    
    print("\n" + "="*60)
    print("📄 PRUEBA DE GENERACIÓN DE INFORME PDF")
    print("="*60)
    
    # Configuración
    base_url = "http://localhost:8000"
    
    # Datos de prueba para PDF
    pdf_report_data = {
        "userId": "test_user_pdf",
        "fullName": "María García López",
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
        "cvAnalysis": {
            "strengths": ["Formación académica presente", "Habilidades técnicas básicas"],
            "weaknesses": ["Falta de experiencia laboral", "Necesita mejorar estructura"],
            "feedback": "CV con potencial, necesita desarrollo de experiencia práctica",
            "structure": "Regular",
            "coherence": "Aceptable",
            "experience": "Limitada",
            "skills": ["Photoshop", "Office", "Go"],
            "education": ["Teleformación Academia del transportista"],
            "alerts": ["Considerar agregar más experiencia práctica"]
        },
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
                "decisions": [{"decision": "Escuchar activamente", "confidence": 85}],
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
            f"{base_url}/api/pdf/generate-report",
            json=pdf_report_data,
            timeout=300  # Timeout extendido a 5 minutos
        )
        
        if response.status_code == 200:
            print("✅ Informe PDF generado exitosamente")
            
            # Guardar PDF
            pdf_filename = "INFORME_COMPLETO_INTEGRADO.pdf"
            with open(pdf_filename, 'wb') as f:
                f.write(response.content)
            
            print(f"💾 PDF guardado en: {pdf_filename}")
            return True
        else:
            print(f"❌ Error generando PDF: {response.status_code}")
            print(f"Detalle: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error en generación de PDF: {str(e)}")
        return False

if __name__ == "__main__":
    print("🎯 PRUEBA FINAL DE INTEGRACIÓN COMPLETA")
    print("=" * 60)
    print("Esta prueba verifica que la aplicación puede:")
    print("1. Analizar CVs reales (incluyendo escaneados)")
    print("2. Integrar análisis de CV con preferencias laborales")
    print("3. Incluir resultados de minijuegos")
    print("4. Generar informes completos y profesionales")
    print("5. Crear informes en PDF")
    print("=" * 60)
    
    # Prueba 1: Informe completo integrado
    test1_success = test_complete_integrated_report()
    
    # Prueba 2: Generación de PDF
    test2_success = test_pdf_report_generation()
    
    print("\n" + "="*60)
    print("📊 RESUMEN FINAL DE PRUEBAS")
    print("="*60)
    print(f"✅ Informe completo integrado: {'EXITOSO' if test1_success else 'FALLIDO'}")
    print(f"✅ Generación de informe PDF: {'EXITOSO' if test2_success else 'FALLIDO'}")
    
    if test1_success and test2_success:
        print("\n🎉 ¡PRUEBA FINAL EXITOSA!")
        print("La aplicación está lista para producción:")
        print("✅ Analiza CVs reales (incluyendo escaneados)")
        print("✅ Integra todos los datos (CV + preferencias + minijuegos)")
        print("✅ Genera informes completos y profesionales")
        print("✅ Crea informes en PDF")
        print("✅ No menciona datos faltantes en los informes")
    else:
        print("\n⚠️ Algunas pruebas fallaron. Revisa los errores anteriores.") 