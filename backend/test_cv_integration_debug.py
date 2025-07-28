#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de debug para verificar la integración completa del CV desde frontend hasta informe final
"""

import json
import sys
import os
from pathlib import Path

# Agregar el directorio actual al path para importar módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_frontend_data_simulation():
    """Simula los datos que envía el frontend al backend"""
    print("🔄 SIMULANDO DATOS DEL FRONTEND")
    print("=" * 50)
    
    # Simular los datos que envía el frontend (basado en ResultadosPage.tsx)
    frontend_data = {
        "userId": "user-ester-2025",
        "fullName": "Ana García",
        "softSkills": [
            {
                "skill": "Comunicación",
                "score": 75,
                "level": "Medio",
                "confidence": 80
            },
            {
                "skill": "Trabajo en equipo",
                "score": 85,
                "level": "Alto",
                "confidence": 90
            },
            {
                "skill": "Resolución de problemas",
                "score": 70,
                "level": "Medio",
                "confidence": 75
            }
        ],
        "cvAnalysis": {
            "strengths": ["Experiencia en desarrollo web", "Conocimientos de Python"],
            "weaknesses": ["Falta de experiencia en gestión de proyectos"],
            "feedback": "CV bien estructurado pero necesita más detalles en proyectos",
            "structure": "Clara y fácil de seguir",
            "coherence": "La experiencia es coherente con los objetivos",
            "experience": "3 años en desarrollo web",
            "skills": ["Python", "JavaScript", "React", "Django"],
            "education": ["Ingeniería Informática", "Curso de Desarrollo Web"],
            "alerts": ["Falta información de contacto", "Periodos sin actividad no explicados"]
        },
        "jobPreferences": {
            "areas": ["Desarrollo web", "Programación"],
            "needs": ["Flexibilidad horaria", "Trabajo remoto"],
            "workMode": "remoto",
            "availability": "completa",
            "willingToRelocate": False,
            "hasDisabilityCert": False
        },
        "completedGames": ["1", "2", "3"],
        "logs": []
    }
    
    print("📤 Datos simulados del frontend:")
    print(f"  • Usuario: {frontend_data['fullName']}")
    print(f"  • Habilidades soft: {len(frontend_data['softSkills'])}")
    print(f"  • CV Analysis: {'✅ Presente' if frontend_data.get('cvAnalysis') else '❌ Ausente'}")
    print(f"  • Preferencias: {'✅ Presentes' if frontend_data.get('jobPreferences') else '❌ Ausentes'}")
    
    return frontend_data

def test_backend_processing():
    """Prueba cómo el backend procesa los datos del frontend"""
    print("\n🔧 PRUEBA DE PROCESAMIENTO EN BACKEND")
    print("=" * 50)
    
    try:
        from main import EmployabilityReportRequest, SoftSkillResult, CvAnalysis, JobPreference
        from generate_report import generar_informe
        
        # Simular datos del frontend
        frontend_data = test_frontend_data_simulation()
        
        # Convertir a objetos Pydantic
        soft_skills = [
            SoftSkillResult(
                skill=skill["skill"],
                score=skill["score"],
                level=skill["level"].lower(),
                confidence=skill["confidence"]
            )
            for skill in frontend_data["softSkills"]
        ]
        
        cv_analysis = CvAnalysis(**frontend_data["cvAnalysis"]) if frontend_data.get("cvAnalysis") else None
        
        job_preferences = JobPreference(**frontend_data["jobPreferences"]) if frontend_data.get("jobPreferences") else None
        
        # Crear request
        request = EmployabilityReportRequest(
            userId=frontend_data["userId"],
            fullName=frontend_data["fullName"],
            softSkills=soft_skills,
            cvAnalysis=cv_analysis,
            jobPreferences=job_preferences,
            completedGames=frontend_data["completedGames"],
            logs=frontend_data["logs"]
        )
        
        print("✅ Datos convertidos a objetos Pydantic")
        print(f"  • CV Analysis: {'✅ Presente' if request.cvAnalysis else '❌ Ausente'}")
        
        # Preparar perfil para la IA
        perfil_texto = f"""
PERFIL COMPLETO DEL CANDIDATO:

DATOS PERSONALES:
- Nombre: {request.fullName}
- ID: {request.userId}

HABILIDADES SOFT EVALUADAS:
{chr(10).join([f"- {skill.skill}: {skill.score}% (Nivel: {skill.level}, Confianza: {skill.confidence}%)" for skill in request.softSkills])}

ANÁLISIS DETALLADO DEL CV:
{format_cv_analysis(request.cvAnalysis.dict()) if request.cvAnalysis else "No se proporcionó análisis de CV"}

PREFERENCIAS LABORALES:
{format_job_preferences(request.jobPreferences.dict()) if request.jobPreferences else "No se especificaron preferencias laborales"}

JUEGOS COMPLETADOS:
{', '.join(request.completedGames) if request.completedGames else "Ningún juego completado"}

LOGS DE JUEGOS:
{json.dumps(request.logs, indent=2, ensure_ascii=False) if request.logs else "No hay logs de juegos disponibles"}
"""
        
        print("📝 Generando informe con datos del frontend...")
        
        # Generar informe
        informe = generar_informe(perfil_texto)
        
        print("✅ Informe generado")
        print(f"📄 Longitud del informe: {len(informe)} caracteres")
        
        # Verificar si el CV se menciona en el informe
        cv_keywords = ["CV", "currículum", "experiencia", "habilidades técnicas", "formación", "Python", "JavaScript", "React", "Django"]
        cv_mentioned = any(keyword.lower() in informe.lower() for keyword in cv_keywords)
        
        print(f"🔍 CV mencionado en informe: {'✅ SÍ' if cv_mentioned else '❌ NO'}")
        
        # Contar menciones específicas del CV
        cv_mentions = 0
        for keyword in cv_keywords:
            if keyword.lower() in informe.lower():
                cv_mentions += 1
        
        print(f"📊 Menciones del CV en informe: {cv_mentions}/{len(cv_keywords)}")
        
        # Mostrar fragmento del informe
        print("\n📄 FRAGMENTO DEL INFORME:")
        lines = informe.split('\n')
        for i, line in enumerate(lines[:15]):  # Primeras 15 líneas
            print(f"{i+1:2d}: {line}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_pdf_generation_with_frontend_data():
    """Prueba la generación del PDF con datos simulados del frontend"""
    print("\n📄 PRUEBA DE GENERACIÓN DE PDF CON DATOS DEL FRONTEND")
    print("=" * 50)
    
    try:
        from pdf_service import create_employability_pdf
        
        # Simular datos del frontend
        frontend_data = test_frontend_data_simulation()
        
        # Preparar datos para el PDF
        pdf_data = {
            "gameData": [
                {
                    "subject": skill["skill"],
                    "dA": skill["score"],
                    "level": skill["level"].lower()
                }
                for skill in frontend_data["softSkills"]
            ],
            "cvAnalysis": frontend_data.get("cvAnalysis", {}),
            "jobPreferences": frontend_data.get("jobPreferences", {}),
            "userInfo": {
                "fullName": frontend_data["fullName"],
                "userId": frontend_data["userId"]
            },
            "informeProfesional": "Informe profesional de prueba generado por IA..."
        }
        
        print("📄 Generando PDF con datos del frontend...")
        
        # Generar PDF
        pdf_content = create_employability_pdf(pdf_data)
        
        print("✅ PDF generado")
        print(f"📄 Tamaño del PDF: {len(pdf_content)} bytes")
        
        # Guardar PDF para verificación
        output_path = "test_informe_frontend_data.pdf"
        with open(output_path, 'wb') as f:
            f.write(pdf_content)
        
        print(f"💾 PDF guardado como: {output_path}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def format_cv_analysis(cv_data: dict) -> str:
    """Formatea el análisis del CV de manera legible para la IA"""
    if not cv_data:
        return "No se proporcionó análisis de CV"
    
    formatted = []
    
    if cv_data.get('strengths'):
        formatted.append("PUNTOS FUERTES:")
        for strength in cv_data['strengths']:
            formatted.append(f"  • {strength}")
        formatted.append("")
    
    if cv_data.get('weaknesses'):
        formatted.append("ÁREAS DE MEJORA:")
        for weakness in cv_data['weaknesses']:
            formatted.append(f"  • {weakness}")
        formatted.append("")
    
    if cv_data.get('feedback'):
        formatted.append(f"FEEDBACK GENERAL: {cv_data['feedback']}")
        formatted.append("")
    
    if cv_data.get('structure'):
        formatted.append(f"ESTRUCTURA: {cv_data['structure']}")
    
    if cv_data.get('coherence'):
        formatted.append(f"COHERENCIA: {cv_data['coherence']}")
    
    if cv_data.get('experience'):
        formatted.append(f"EXPERIENCIA: {cv_data['experience']}")
    
    if cv_data.get('skills'):
        formatted.append("HABILIDADES TÉCNICAS DETECTADAS:")
        for skill in cv_data['skills']:
            formatted.append(f"  • {skill}")
        formatted.append("")
    
    if cv_data.get('education'):
        formatted.append("FORMACIÓN DETECTADA:")
        for edu in cv_data['education']:
            formatted.append(f"  • {edu}")
        formatted.append("")
    
    if cv_data.get('alerts'):
        formatted.append("ALERTAS O PUNTOS CRÍTICOS:")
        for alert in cv_data['alerts']:
            formatted.append(f"  ⚠️ {alert}")
        formatted.append("")
    
    return "\n".join(formatted) if formatted else "Análisis de CV disponible pero sin detalles específicos"

def format_job_preferences(preferences: dict) -> str:
    """Formatea las preferencias laborales de manera legible para la IA"""
    if not preferences:
        return "No se especificaron preferencias laborales"
    
    formatted = []
    
    if preferences.get('areas'):
        formatted.append("ÁREAS DE INTERÉS:")
        for area in preferences['areas']:
            formatted.append(f"  • {area}")
        formatted.append("")
    
    if preferences.get('needs'):
        formatted.append("NECESIDADES ESPECÍFICAS:")
        for need in preferences['needs']:
            formatted.append(f"  • {need}")
        formatted.append("")
    
    if preferences.get('workMode'):
        formatted.append(f"MODO DE TRABAJO: {preferences['workMode']}")
    
    if preferences.get('availability'):
        formatted.append(f"DISPONIBILIDAD: {preferences['availability']}")
    
    return "\n".join(formatted) if formatted else "No se especificaron preferencias laborales"

def main():
    """Ejecuta todas las pruebas de integración"""
    print("🚀 INICIANDO PRUEBAS DE INTEGRACIÓN DEL CV")
    print("=" * 60)
    
    # Prueba 1: Simulación de datos del frontend
    test1_success = test_frontend_data_simulation()
    
    # Prueba 2: Procesamiento en backend
    test2_success = test_backend_processing()
    
    # Prueba 3: Generación de PDF con datos del frontend
    test3_success = test_pdf_generation_with_frontend_data()
    
    # Resumen
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE PRUEBAS DE INTEGRACIÓN:")
    print(f"  • Datos del frontend: {'✅ EXITOSOS' if test1_success else '❌ FALLIDOS'}")
    print(f"  • Procesamiento backend: {'✅ EXITOSO' if test2_success else '❌ FALLIDO'}")
    print(f"  • Generación PDF: {'✅ EXITOSA' if test3_success else '❌ FALLIDA'}")
    
    if all([test1_success, test2_success, test3_success]):
        print("\n🎉 TODAS LAS PRUEBAS DE INTEGRACIÓN EXITOSAS")
        print("💡 El análisis del CV se está integrando correctamente")
        print("🔍 Si el informe no muestra datos del CV, el problema puede estar en:")
        print("   • La configuración de Azure OpenAI")
        print("   • El prompt de la IA")
        print("   • El procesamiento del informe final")
    else:
        print("\n⚠️ ALGUNAS PRUEBAS FALLARON")
        print("🔧 Revisar los errores anteriores")

if __name__ == "__main__":
    main() 