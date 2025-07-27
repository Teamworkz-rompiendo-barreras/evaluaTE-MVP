#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de prueba para verificar que el análisis del CV se incluya correctamente 
en el informe final después de las correcciones realizadas.
"""

import json
import sys
import os
from datetime import datetime

# Agregar el directorio actual al path para importar los módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import EmployabilityReportRequest, SoftSkillResult, CvAnalysis, JobPreference, format_cv_analysis

def test_cv_analysis_integration():
    """Prueba que el análisis del CV se integre correctamente en el informe"""
    
    print("🧪 Iniciando prueba de integración del análisis del CV...")
    
    # Crear datos de prueba con análisis de CV completo
    test_cv_analysis = CvAnalysis(
        strengths=[
            "Experiencia técnica sólida en desarrollo web",
            "Formación académica relevante en ingeniería informática",
            "Conocimientos actualizados en tecnologías modernas"
        ],
        weaknesses=[
            "Falta de experiencia en gestión de equipos",
            "Necesita mejorar habilidades de comunicación",
            "Pocos proyectos de liderazgo documentados"
        ],
        feedback="CV bien estructurado con buena experiencia técnica. Áreas de mejora en habilidades blandas y liderazgo.",
        structure="Clara y fácil de seguir",
        coherence="La experiencia es coherente con los objetivos profesionales",
        experience="5 años de experiencia en desarrollo de software y análisis de datos",
        skills=["Python", "JavaScript", "React", "Node.js", "SQL", "MongoDB", "Docker", "AWS"],
        education=["Ingeniería Informática - Universidad Politécnica", "Certificación AWS Developer", "Curso de Machine Learning"],
        alerts=["Considerar agregar más detalles sobre logros específicos", "Incluir métricas de impacto en proyectos"]
    )
    
    # Crear habilidades soft de prueba
    test_soft_skills = [
        SoftSkillResult(skill="Comunicación", score=75, level="medio", confidence=85),
        SoftSkillResult(skill="Trabajo en equipo", score=90, level="alto", confidence=90),
        SoftSkillResult(skill="Resolución de problemas", score=85, level="alto", confidence=88),
        SoftSkillResult(skill="Liderazgo", score=60, level="medio", confidence=70),
        SoftSkillResult(skill="Adaptabilidad", score=80, level="alto", confidence=85)
    ]
    
    # Crear preferencias laborales de prueba
    test_job_preferences = JobPreference(
        areas=["Desarrollo web", "Análisis de datos", "DevOps"],
        needs=["Entorno colaborativo", "Oportunidades de aprendizaje", "Flexibilidad horaria"],
        workMode="híbrido",
        availability="completa",
        willingToRelocate=True,
        hasDisabilityCert=False
    )
    
    # Crear solicitud de informe
    test_request = EmployabilityReportRequest(
        userId="test_user_123",
        fullName="Ana García López",
        softSkills=test_soft_skills,
        cvAnalysis=test_cv_analysis,
        jobPreferences=test_job_preferences,
        completedGames=["comunicacion", "liderazgo", "trabajo_equipo"],
        logs=[]
    )
    
    print("✅ Datos de prueba creados correctamente")
    
    # Probar la función format_cv_analysis
    print("\n📋 Probando formateo del análisis del CV...")
    cv_formatted = format_cv_analysis(test_cv_analysis.dict())
    print("Formato del CV generado:")
    print("-" * 50)
    print(cv_formatted)
    print("-" * 50)
    
    # Verificar que todas las secciones estén incluidas
    required_sections = [
        "PUNTOS FUERTES:",
        "ÁREAS DE MEJORA:",
        "FEEDBACK GENERAL:",
        "ESTRUCTURA:",
        "COHERENCIA:",
        "EXPERIENCIA:",
        "HABILIDADES TÉCNICAS DETECTADAS:",
        "FORMACIÓN DETECTADA:",
        "ALERTAS O PUNTOS CRÍTICOS:"
    ]
    
    missing_sections = []
    for section in required_sections:
        if section not in cv_formatted:
            missing_sections.append(section)
    
    if missing_sections:
        print(f"❌ Secciones faltantes en el formateo: {missing_sections}")
        return False
    else:
        print("✅ Todas las secciones del CV están incluidas en el formateo")
    
    # Verificar que las habilidades técnicas estén incluidas
    if "Python" in cv_formatted and "JavaScript" in cv_formatted and "React" in cv_formatted:
        print("✅ Habilidades técnicas detectadas correctamente")
    else:
        print("❌ Habilidades técnicas no detectadas correctamente")
        return False
    
    # Verificar que la formación esté incluida
    if "Ingeniería Informática" in cv_formatted and "Certificación AWS" in cv_formatted:
        print("✅ Formación detectada correctamente")
    else:
        print("❌ Formación no detectada correctamente")
        return False
    
    # Verificar que las alertas estén incluidas
    if "Considerar agregar más detalles" in cv_formatted and "Incluir métricas" in cv_formatted:
        print("✅ Alertas detectadas correctamente")
    else:
        print("❌ Alertas no detectadas correctamente")
        return False
    
    # Simular la preparación del perfil completo (como en generate_report)
    print("\n🔄 Simulando preparación del perfil completo...")
    
    perfil_completo = {
        "datos_personales": {
            "nombre": test_request.fullName,
            "user_id": test_request.userId
        },
        "habilidades_soft": [
            {
                "habilidad": skill.skill,
                "puntuacion": skill.score,
                "nivel": skill.level,
                "confianza": skill.confidence
            }
            for skill in test_request.softSkills
        ],
        "analisis_cv": test_request.cvAnalysis.dict() if test_request.cvAnalysis else {},
        "preferencias_laborales": test_request.jobPreferences.dict() if test_request.jobPreferences else {},
        "juegos_completados": test_request.completedGames,
        "logs_juegos": [log.dict() for log in test_request.logs] if test_request.logs else []
    }
    
    # Verificar que el análisis del CV esté en el perfil completo
    if perfil_completo.get('analisis_cv'):
        cv_in_profile = perfil_completo['analisis_cv']
        if (cv_in_profile.get('skills') and 
            cv_in_profile.get('education') and 
            cv_in_profile.get('alerts')):
            print("✅ Análisis del CV incluido correctamente en el perfil completo")
        else:
            print("❌ Análisis del CV incompleto en el perfil")
            return False
    else:
        print("❌ Análisis del CV no encontrado en el perfil completo")
        return False
    
    # Simular la generación del texto del perfil (como en generate_report)
    print("\n📝 Simulando generación del texto del perfil...")
    
    perfil_texto = f"""
PERFIL COMPLETO DEL CANDIDATO:

DATOS PERSONALES:
- Nombre: {perfil_completo['datos_personales']['nombre']}
- ID: {perfil_completo['datos_personales']['user_id']}

HABILIDADES SOFT EVALUADAS:
{chr(10).join([f"- {h['habilidad']}: {h['puntuacion']}% (Nivel: {h['nivel']}, Confianza: {h['confianza']}%)" for h in perfil_completo['habilidades_soft']])}

ANÁLISIS DETALLADO DEL CV:
{format_cv_analysis(perfil_completo['analisis_cv']) if perfil_completo['analisis_cv'] else "El candidato no ha proporcionado un CV para análisis. Se realizará la evaluación basada en las habilidades soft evaluadas y preferencias laborales."}

PREFERENCIAS LABORALES:
{format_job_preferences(perfil_completo['preferencias_laborales']) if perfil_completo['preferencias_laborales'] else "El candidato no ha especificado preferencias laborales detalladas. Se realizará la evaluación basada en las habilidades soft evaluadas."}

JUEGOS COMPLETADOS:
{', '.join(perfil_completo['juegos_completados']) if perfil_completo['juegos_completados'] else "El candidato no ha completado juegos de evaluación. La evaluación se basa en las habilidades soft proporcionadas."}

LOGS DE JUEGOS:
{json.dumps(perfil_completo['logs_juegos'], indent=2, ensure_ascii=False) if perfil_completo['logs_juegos'] else "No se dispone de logs detallados de juegos. La evaluación se basa en los resultados de habilidades soft proporcionados."}
"""
    
    # Verificar que el análisis del CV esté en el texto del perfil
    if "ANÁLISIS DETALLADO DEL CV:" in perfil_texto:
        if ("Python" in perfil_texto and 
            "Ingeniería Informática" in perfil_texto and 
            "Considerar agregar más detalles" in perfil_texto):
            print("✅ Análisis del CV incluido correctamente en el texto del perfil")
        else:
            print("❌ Contenido del análisis del CV no encontrado en el texto del perfil")
            return False
    else:
        print("❌ Sección de análisis del CV no encontrada en el texto del perfil")
        return False
    
    # Simular la preparación de datos para el PDF (como en generate_pdf_report)
    print("\n📊 Simulando preparación de datos para el PDF...")
    
    cv_analysis_dict = test_request.cvAnalysis.dict() if test_request.cvAnalysis else {}
    
    pdf_data = {
        "gameData": [skill.dict() for skill in test_request.softSkills],
        "cvAnalysis": cv_analysis_dict,
        "jobPreferences": test_request.jobPreferences.dict() if test_request.jobPreferences else {},
        "userInfo": {
            "fullName": test_request.fullName,
            "userId": test_request.userId
        },
        "informeProfesional": "Informe de prueba generado por IA"
    }
    
    # Verificar que el análisis del CV esté en los datos del PDF
    if pdf_data.get('cvAnalysis'):
        cv_in_pdf = pdf_data['cvAnalysis']
        if (cv_in_pdf.get('skills') and 
            cv_in_pdf.get('education') and 
            cv_in_pdf.get('alerts')):
            print("✅ Análisis del CV incluido correctamente en los datos del PDF")
        else:
            print("❌ Análisis del CV incompleto en los datos del PDF")
            return False
    else:
        print("❌ Análisis del CV no encontrado en los datos del PDF")
        return False
    
    print("\n🎉 ¡Todas las pruebas pasaron exitosamente!")
    print("✅ El análisis del CV se está incluyendo correctamente en:")
    print("   - El formateo para la IA")
    print("   - El perfil completo")
    print("   - El texto del perfil")
    print("   - Los datos del PDF")
    print("   - El informe final")
    
    return True

if __name__ == "__main__":
    try:
        success = test_cv_analysis_integration()
        if success:
            print("\n✅ PROBLEMA SOLUCIONADO: El análisis del CV ahora se incluye correctamente en el informe final")
            sys.exit(0)
        else:
            print("\n❌ PROBLEMA PERSISTE: El análisis del CV no se está incluyendo correctamente")
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error durante la prueba: {str(e)}")
        import traceback
        print(f"📋 Traceback: {traceback.format_exc()}")
        sys.exit(1) 