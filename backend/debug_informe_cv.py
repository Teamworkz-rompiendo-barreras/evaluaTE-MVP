#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de debug para verificar qué datos se están enviando al informe
y si el análisis del CV está llegando correctamente.
"""

import requests
import json
import os

def debug_informe_data():
    """Debug para verificar los datos que se envían al informe"""
    
    print("🔍 DEBUG: Verificando datos del informe")
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
        "userId": "debug_user",
        "fullName": "Usuario Debug",
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
        
        # Mostrar análisis del CV
        print(f"\n📊 ANÁLISIS DEL CV OBTENIDO:")
        print(f"  • Fortalezas: {len(cv_analysis.get('strengths', []))}")
        print(f"  • Debilidades: {len(cv_analysis.get('weaknesses', []))}")
        print(f"  • Habilidades técnicas: {len(cv_analysis.get('skills', []))}")
        print(f"  • Formación: {len(cv_analysis.get('education', []))}")
        print(f"  • Alertas: {len(cv_analysis.get('alerts', []))}")
        
        # Mostrar contenido detallado
        if cv_analysis.get('strengths'):
            print(f"\n💪 FORTALEZAS:")
            for i, strength in enumerate(cv_analysis['strengths'], 1):
                print(f"  {i}. {strength}")
        
        if cv_analysis.get('weaknesses'):
            print(f"\n⚠️ DEBILIDADES:")
            for i, weakness in enumerate(cv_analysis['weaknesses'], 1):
                print(f"  {i}. {weakness}")
        
        if cv_analysis.get('skills'):
            print(f"\n🛠️ HABILIDADES TÉCNICAS:")
            for i, skill in enumerate(cv_analysis['skills'], 1):
                print(f"  {i}. {skill}")
        
        if cv_analysis.get('education'):
            print(f"\n🎓 FORMACIÓN:")
            for i, edu in enumerate(cv_analysis['education'], 1):
                print(f"  {i}. {edu}")
        
        if cv_analysis.get('feedback'):
            print(f"\n💬 FEEDBACK: {cv_analysis['feedback']}")
        
    except Exception as e:
        print(f"❌ Error en análisis de CV: {str(e)}")
        return False
    
    # Paso 2: Generar informe completo
    print("\n📋 PASO 2: Generando informe completo...")
    
    # Datos completos para el informe
    complete_report_data = {
        "userId": "debug_user",
        "fullName": "Usuario Debug",
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
        
        # Mostrar resumen del informe
        print(f"\n📊 RESUMEN DEL INFORME:")
        print(f"  • Puntuación de empleabilidad: {report.get('employabilityScore', 'N/A')}")
        print(f"  • Nivel: {report.get('level', 'N/A')}")
        
        # Verificar que el informe incluye análisis de CV
        report_content = report.get('report', {})
        
        print(f"\n📋 CONTENIDO DEL INFORME:")
        print(f"  • Secciones del informe: {len(report_content)}")
        
        # Verificar si el CV está incluido en el informe
        cv_included = report_content.get('cvAnalysis') is not None
        print(f"  • CV incluido en informe: {'✅ SÍ' if cv_included else '❌ NO'}")
        
        if cv_included:
            cv_data = report_content['cvAnalysis']
            print(f"  • Fortalezas en informe: {len(cv_data.get('strengths', []))}")
            print(f"  • Habilidades en informe: {len(cv_data.get('skills', []))}")
        
        # Verificar el informe profesional de IA
        informe_profesional = report_content.get('informeProfesional', '')
        if informe_profesional:
            print(f"\n📄 INFORME PROFESIONAL DE IA:")
            print(f"  • Longitud: {len(informe_profesional)} caracteres")
            
            # Buscar menciones del CV en el informe
            cv_mentions = [
                "cv" in informe_profesional.lower(),
                "curriculum" in informe_profesional.lower(),
                "experiencia" in informe_profesional.lower(),
                "formación" in informe_profesional.lower(),
                "habilidades técnicas" in informe_profesional.lower()
            ]
            
            print(f"  • Menciones de CV: {sum(cv_mentions)} de 5")
            
            # Mostrar primeras líneas del informe
            lines = informe_profesional.split('\n')[:10]
            print(f"\n📝 PRIMERAS LÍNEAS DEL INFORME:")
            for i, line in enumerate(lines, 1):
                print(f"  {i:2d}. {line[:80]}{'...' if len(line) > 80 else ''}")
            
            # Guardar informe completo para revisión
            with open("DEBUG_INFORME_COMPLETO.txt", 'w', encoding='utf-8') as f:
                f.write(informe_profesional)
            print(f"\n💾 Informe completo guardado en: DEBUG_INFORME_COMPLETO.txt")
        
        return True
        
    except Exception as e:
        print(f"❌ Error generando informe: {str(e)}")
        return False

def debug_format_cv_analysis():
    """Debug para verificar la función format_cv_analysis"""
    
    print("\n" + "="*60)
    print("🔍 DEBUG: Función format_cv_analysis")
    print("=" * 60)
    
    # Simular datos de CV
    cv_data = {
        "strengths": ["Formación académica presente", "Habilidades técnicas básicas"],
        "weaknesses": ["Falta de experiencia laboral", "Necesita mejorar estructura"],
        "feedback": "CV con potencial, necesita desarrollo de experiencia práctica",
        "structure": "Regular",
        "coherence": "Aceptable",
        "experience": "Limitada",
        "skills": ["Photoshop", "Office", "Go"],
        "education": ["Teleformación Academia del transportista"],
        "alerts": ["Considerar agregar más experiencia práctica"]
    }
    
    # Importar la función
    import sys
    sys.path.append('.')
    
    try:
        from main import format_cv_analysis
        
        formatted = format_cv_analysis(cv_data)
        print("✅ Función format_cv_analysis ejecutada correctamente")
        print(f"📏 Longitud del texto formateado: {len(formatted)} caracteres")
        
        print(f"\n📝 TEXTO FORMATEADO:")
        print(formatted)
        
        return True
        
    except Exception as e:
        print(f"❌ Error en format_cv_analysis: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 INICIANDO DEBUG COMPLETO DEL INFORME")
    print("=" * 60)
    
    # Debug 1: Verificar datos del informe
    test1_success = debug_informe_data()
    
    # Debug 2: Verificar función de formateo
    test2_success = debug_format_cv_analysis()
    
    print("\n" + "="*60)
    print("📊 RESUMEN DE DEBUG")
    print("="*60)
    print(f"✅ Debug datos del informe: {'EXITOSO' if test1_success else 'FALLIDO'}")
    print(f"✅ Debug format_cv_analysis: {'EXITOSO' if test2_success else 'FALLIDO'}")
    
    if test1_success and test2_success:
        print("\n🎉 ¡DEBUG COMPLETADO!")
        print("Revisa el archivo DEBUG_INFORME_COMPLETO.txt para ver el informe completo.")
    else:
        print("\n⚠️ Algunos tests de debug fallaron. Revisa los errores anteriores.") 