#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para debuggear el estado del frontend y verificar por qué no se envían los datos correctamente
"""

import json
import sys
import os
from pathlib import Path

# Agregar el directorio actual al path para importar módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_frontend_state_simulation():
    """Simula el estado del frontend para identificar el problema"""
    print("🔍 DEBUGGEANDO ESTADO DEL FRONTEND")
    print("=" * 50)
    
    # Simular diferentes estados del frontend
    test_cases = [
        {
            "name": "Estado completo con CV",
            "report": {
                "userId": "user-ester-2025",
                "firstName": "Ana",
                "lastName": "García",
                "softSkills": [
                    {"skill": "Comunicación", "score": 75, "level": "Medio", "confidence": 80},
                    {"skill": "Trabajo en equipo", "score": 85, "level": "Alto", "confidence": 90},
                    {"skill": "Resolución de problemas", "score": 70, "level": "Medio", "confidence": 75}
                ],
                "jobPreferences": {
                    "areas": ["Desarrollo web", "Programación"],
                    "needs": ["Flexibilidad horaria", "Trabajo remoto"],
                    "workMode": "remoto",
                    "availability": "completa"
                },
                "employabilityScore": 80
            },
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
            "game": {
                "completedGames": ["1", "2", "3"]
            }
        },
        {
            "name": "Estado sin CV",
            "report": {
                "userId": "user-ester-2025",
                "firstName": "Ana",
                "lastName": "García",
                "softSkills": [
                    {"skill": "Comunicación", "score": 75, "level": "Medio", "confidence": 80},
                    {"skill": "Trabajo en equipo", "score": 85, "level": "Alto", "confidence": 90}
                ],
                "jobPreferences": {
                    "areas": ["Desarrollo web"],
                    "needs": ["Flexibilidad horaria"],
                    "workMode": "remoto",
                    "availability": "completa"
                },
                "employabilityScore": 80
            },
            "cvAnalysis": None,
            "game": {
                "completedGames": ["1", "2"]
            }
        },
        {
            "name": "Estado sin preferencias laborales",
            "report": {
                "userId": "user-ester-2025",
                "firstName": "Ana",
                "lastName": "García",
                "softSkills": [
                    {"skill": "Comunicación", "score": 75, "level": "Medio", "confidence": 80}
                ],
                "jobPreferences": None,
                "employabilityScore": 75
            },
            "cvAnalysis": {
                "strengths": ["Experiencia en desarrollo web"],
                "weaknesses": ["Falta de experiencia"],
                "feedback": "CV básico",
                "structure": "regular",
                "coherence": "regular",
                "experience": "2 años",
                "skills": ["Python"],
                "education": ["Ingeniería"],
                "alerts": []
            },
            "game": {
                "completedGames": ["1"]
            }
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 PRUEBA {i}: {test_case['name']}")
        print("-" * 30)
        
        # Verificar condiciones del frontend
        report = test_case['report']
        cv_analysis = test_case['cvAnalysis']
        game = test_case['game']
        
        # Condición 1: report?.jobPreferences && report?.softSkills
        has_job_preferences = bool(report.get('jobPreferences'))
        has_soft_skills = bool(report.get('softSkills') and len(report['softSkills']) > 0)
        
        print(f"  • Tiene jobPreferences: {'✅ SÍ' if has_job_preferences else '❌ NO'}")
        print(f"  • Tiene softSkills: {'✅ SÍ' if has_soft_skills else '❌ NO'}")
        print(f"  • Condición fetchIaReport: {'✅ CUMPLIDA' if (has_job_preferences and has_soft_skills) else '❌ NO CUMPLIDA'}")
        
        # Simular el requestBody que se enviaría
        request_body = {
            "userId": report.get('userId', 'user'),
            "fullName": f"{report.get('firstName', '')} {report.get('lastName', '')}".strip() or 'Usuario',
            "softSkills": [
                {
                    "skill": skill["skill"],
                    "score": skill["score"],
                    "level": skill["level"],
                    "confidence": skill["confidence"]
                }
                for skill in (report.get('softSkills') or [])
            ],
            "cvAnalysis": cv_analysis,
            "jobPreferences": report.get('jobPreferences'),
            "completedGames": game.get('completedGames', []),
            "logs": []
        }
        
        print(f"  • Datos en requestBody:")
        print(f"    - softSkills: {len(request_body['softSkills'])} elementos")
        print(f"    - cvAnalysis: {'✅ Presente' if request_body['cvAnalysis'] else '❌ Ausente'}")
        print(f"    - jobPreferences: {'✅ Presentes' if request_body['jobPreferences'] else '❌ Ausentes'}")
        print(f"    - completedGames: {len(request_body['completedGames'])} juegos")
        
        # Verificar si se enviaría al backend
        if has_job_preferences and has_soft_skills:
            print("  ✅ SE ENVIARÍA AL BACKEND")
        else:
            print("  ❌ NO SE ENVIARÍA AL BACKEND")
    
    return test_cases

def test_backend_response_simulation():
    """Simula las respuestas del backend para diferentes estados"""
    print("\n🔧 SIMULANDO RESPUESTAS DEL BACKEND")
    print("=" * 50)
    
    try:
        from main import EmployabilityReportRequest, SoftSkillResult, CvAnalysis, JobPreference
        from generate_report import generar_informe
        
        # Usar el primer caso de prueba (estado completo)
        test_cases = test_frontend_state_simulation()
        test_case = test_cases[0]  # Estado completo con CV
        
        print(f"📤 Probando con: {test_case['name']}")
        
        # Convertir a objetos Pydantic
        soft_skills = [
            SoftSkillResult(
                skill=skill["skill"],
                score=skill["score"],
                level=skill["level"].lower(),
                confidence=skill["confidence"]
            )
            for skill in test_case['report']['softSkills']
        ]
        
        cv_analysis = CvAnalysis(**test_case['cvAnalysis']) if test_case['cvAnalysis'] else None
        
        job_preferences = JobPreference(**test_case['report']['jobPreferences']) if test_case['report'].get('jobPreferences') else None
        
        # Crear request
        request = EmployabilityReportRequest(
            userId=test_case['report']['userId'],
            fullName=f"{test_case['report']['firstName']} {test_case['report']['lastName']}",
            softSkills=soft_skills,
            cvAnalysis=cv_analysis,
            jobPreferences=job_preferences,
            completedGames=test_case['game']['completedGames'],
            logs=[]
        )
        
        print("✅ Request creado correctamente")
        print(f"  • CV Analysis: {'✅ Presente' if request.cvAnalysis else '❌ Ausente'}")
        print(f"  • Job Preferences: {'✅ Presentes' if request.jobPreferences else '❌ Ausentes'}")
        print(f"  • Soft Skills: {len(request.softSkills)} elementos")
        
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
No hay logs de juegos disponibles
"""
        
        print("📝 Generando informe...")
        
        # Generar informe
        informe = generar_informe(perfil_texto)
        
        print("✅ Informe generado")
        print(f"📄 Longitud del informe: {len(informe)} caracteres")
        
        # Verificar contenido del informe
        cv_keywords = ["CV", "currículum", "experiencia", "habilidades técnicas", "formación", "Python", "JavaScript", "React", "Django"]
        cv_mentions = sum(1 for keyword in cv_keywords if keyword.lower() in informe.lower())
        
        print(f"🔍 Menciones del CV en informe: {cv_mentions}/{len(cv_keywords)}")
        
        # Simular respuesta del backend
        backend_response = {
            "report": {
                "informeProfesional": informe,
                "userId": request.userId,
                "fullName": request.fullName,
                "softSkills": [skill.dict() for skill in request.softSkills],
                "cvAnalysis": request.cvAnalysis.dict() if request.cvAnalysis else None,
                "jobPreferences": request.jobPreferences.dict() if request.jobPreferences else None,
                "employabilityScore": 85,
                "level": "alto",
                "createdAt": "2025-01-27T10:00:00Z"
            },
            "recommendations": {
                "roles": ["Desarrollador Frontend", "Soporte Técnico"],
                "resources": ["Curso de React", "Tutorial de Django"],
                "cvImprovements": ["Agregar más detalles de proyectos"],
                "nextSteps": ["Actualizar CV", "Buscar oportunidades"]
            },
            "employabilityScore": 85,
            "level": "alto",
            "summary": "Perfil con buenas habilidades técnicas y experiencia relevante",
            "createdAt": "2025-01-27T10:00:00Z"
        }
        
        print("✅ Respuesta del backend simulada")
        print(f"  • Informe profesional: {'✅ Presente' if backend_response['report'].get('informeProfesional') else '❌ Ausente'}")
        print(f"  • CV Analysis en respuesta: {'✅ Presente' if backend_response['report'].get('cvAnalysis') else '❌ Ausente'}")
        
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
    """Ejecuta el debug del estado del frontend"""
    print("🚀 INICIANDO DEBUG DEL ESTADO DEL FRONTEND")
    print("=" * 60)
    
    # Prueba 1: Simulación de estados del frontend
    test1_success = test_frontend_state_simulation()
    
    # Prueba 2: Simulación de respuestas del backend
    test2_success = test_backend_response_simulation()
    
    # Resumen
    print("\n" + "=" * 60)
    print("📊 RESUMEN DEL DEBUG:")
    print(f"  • Estados del frontend: {'✅ ANALIZADOS' if test1_success else '❌ ERROR'}")
    print(f"  • Respuestas del backend: {'✅ SIMULADAS' if test2_success else '❌ ERROR'}")
    
    print("\n💡 DIAGNÓSTICO:")
    print("El problema 'no hay datos suficientes' puede deberse a:")
    print("1. ❌ report?.jobPreferences es null/undefined")
    print("2. ❌ report?.softSkills es null/undefined o array vacío")
    print("3. ❌ La condición if (report?.jobPreferences && report?.softSkills) no se cumple")
    print("4. ❌ Los datos no se están guardando correctamente en Redux")
    
    print("\n🔧 SOLUCIONES POSIBLES:")
    print("1. Verificar que savePreferences se ejecute correctamente")
    print("2. Verificar que saveSoftSkills se ejecute correctamente")
    print("3. Verificar que generateFinalReport se ejecute correctamente")
    print("4. Agregar logs en el frontend para debuggear el estado")

if __name__ == "__main__":
    main() 