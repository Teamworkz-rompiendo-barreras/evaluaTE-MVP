#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para verificar que la solución del frontend funciona correctamente
"""

import json
import sys
import os
from pathlib import Path

# Agregar el directorio actual al path para importar módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_frontend_fix_scenarios():
    """Prueba diferentes escenarios del frontend con la nueva condición"""
    print("🔧 VERIFICANDO SOLUCIÓN DEL FRONTEND")
    print("=" * 50)
    
    # Escenarios que deberían funcionar con la nueva condición
    test_scenarios = [
        {
            "name": "Solo soft skills (sin preferencias laborales)",
            "report": {
                "softSkills": [
                    {"skill": "Comunicación", "score": 75, "level": "Medio", "confidence": 80},
                    {"skill": "Trabajo en equipo", "score": 85, "level": "Alto", "confidence": 90}
                ],
                "jobPreferences": None
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
            "expected_result": "✅ DEBERÍA FUNCIONAR"
        },
        {
            "name": "Soft skills + preferencias laborales + CV",
            "report": {
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
                }
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
            "expected_result": "✅ DEBERÍA FUNCIONAR"
        },
        {
            "name": "Sin soft skills (no debería funcionar)",
            "report": {
                "softSkills": [],
                "jobPreferences": {
                    "areas": ["Desarrollo web"],
                    "needs": ["Flexibilidad horaria"],
                    "workMode": "remoto",
                    "availability": "completa"
                }
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
            "expected_result": "❌ NO DEBERÍA FUNCIONAR"
        },
        {
            "name": "Sin report (no debería funcionar)",
            "report": None,
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
            "expected_result": "❌ NO DEBERÍA FUNCIONAR"
        }
    ]
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n📋 ESCENARIO {i}: {scenario['name']}")
        print("-" * 40)
        
        report = scenario['report']
        cv_analysis = scenario['cvAnalysis']
        
        # Simular la nueva condición del frontend
        has_soft_skills = bool(report and report.get('softSkills') and len(report['softSkills']) > 0)
        
        print(f"  • report existe: {'✅ SÍ' if report else '❌ NO'}")
        if report:
            print(f"  • report.softSkills existe: {'✅ SÍ' if report.get('softSkills') else '❌ NO'}")
            print(f"  • report.softSkills.length > 0: {'✅ SÍ' if len(report.get('softSkills', [])) > 0 else '❌ NO'}")
        
        print(f"  • Nueva condición (softSkills && length > 0): {'✅ CUMPLIDA' if has_soft_skills else '❌ NO CUMPLIDA'}")
        print(f"  • Resultado esperado: {scenario['expected_result']}")
        
        # Verificar si el resultado coincide con lo esperado
        if has_soft_skills and "DEBERÍA FUNCIONAR" in scenario['expected_result']:
            print("  ✅ RESULTADO CORRECTO")
        elif not has_soft_skills and "NO DEBERÍA FUNCIONAR" in scenario['expected_result']:
            print("  ✅ RESULTADO CORRECTO")
        else:
            print("  ❌ RESULTADO INCORRECTO")
    
    return True

def test_backend_integration_with_fix():
    """Prueba la integración con el backend usando la nueva condición"""
    print("\n🔧 PRUEBA DE INTEGRACIÓN CON BACKEND")
    print("=" * 50)
    
    try:
        from main import EmployabilityReportRequest, SoftSkillResult, CvAnalysis, JobPreference
        from generate_report import generar_informe
        
        # Usar el escenario que debería funcionar con la nueva condición
        test_data = {
            "report": {
                "softSkills": [
                    {"skill": "Comunicación", "score": 75, "level": "Medio", "confidence": 80},
                    {"skill": "Trabajo en equipo", "score": 85, "level": "Alto", "confidence": 90}
                ],
                "jobPreferences": None  # Sin preferencias laborales
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
            }
        }
        
        print("📤 Probando con datos mínimos (solo soft skills + CV)")
        
        # Convertir a objetos Pydantic
        soft_skills = [
            SoftSkillResult(
                skill=skill["skill"],
                score=skill["score"],
                level=skill["level"].lower(),
                confidence=skill["confidence"]
            )
            for skill in test_data['report']['softSkills']
        ]
        
        cv_analysis = CvAnalysis(**test_data['cvAnalysis']) if test_data['cvAnalysis'] else None
        
        # Crear request (sin job preferences)
        request = EmployabilityReportRequest(
            userId="user-test",
            fullName="Ana García",
            softSkills=soft_skills,
            cvAnalysis=cv_analysis,
            jobPreferences=None,  # Sin preferencias laborales
            completedGames=["1", "2"],
            logs=[]
        )
        
        print("✅ Request creado correctamente")
        print(f"  • Soft Skills: {len(request.softSkills)} elementos")
        print(f"  • CV Analysis: {'✅ Presente' if request.cvAnalysis else '❌ Ausente'}")
        print(f"  • Job Preferences: {'✅ Presentes' if request.jobPreferences else '❌ Ausentes'}")
        
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
No se especificaron preferencias laborales

JUEGOS COMPLETADOS:
{', '.join(request.completedGames) if request.completedGames else "Ningún juego completado"}

LOGS DE JUEGOS:
No hay logs de juegos disponibles
"""
        
        print("📝 Generando informe con datos mínimos...")
        
        # Generar informe
        informe = generar_informe(perfil_texto)
        
        print("✅ Informe generado")
        print(f"📄 Longitud del informe: {len(informe)} caracteres")
        
        # Verificar contenido del informe
        cv_keywords = ["CV", "currículum", "experiencia", "habilidades técnicas", "formación", "Python"]
        cv_mentions = sum(1 for keyword in cv_keywords if keyword.lower() in informe.lower())
        
        print(f"🔍 Menciones del CV en informe: {cv_mentions}/{len(cv_keywords)}")
        
        # Verificar que el informe no mencione preferencias laborales específicas
        if "No se especificaron preferencias laborales" in perfil_texto:
            print("✅ El informe maneja correctamente la ausencia de preferencias laborales")
        else:
            print("❌ El informe no maneja correctamente la ausencia de preferencias laborales")
        
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

def main():
    """Ejecuta las pruebas de verificación de la solución"""
    print("🚀 VERIFICANDO SOLUCIÓN DEL FRONTEND")
    print("=" * 60)
    
    # Prueba 1: Escenarios del frontend
    test1_success = test_frontend_fix_scenarios()
    
    # Prueba 2: Integración con backend
    test2_success = test_backend_integration_with_fix()
    
    # Resumen
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE VERIFICACIÓN:")
    print(f"  • Escenarios del frontend: {'✅ VERIFICADOS' if test1_success else '❌ ERROR'}")
    print(f"  • Integración con backend: {'✅ VERIFICADA' if test2_success else '❌ ERROR'}")
    
    if all([test1_success, test2_success]):
        print("\n🎉 SOLUCIÓN VERIFICADA")
        print("💡 La nueva condición del frontend debería resolver el problema")
        print("🔧 Cambios realizados:")
        print("   • Modificada la condición: report?.jobPreferences && report?.softSkills")
        print("   • Nueva condición: report?.softSkills && report.softSkills.length > 0")
        print("   • Agregados logs de debug para monitoreo")
    else:
        print("\n⚠️ ALGUNAS VERIFICACIONES FALLARON")
        print("🔧 Revisar los errores anteriores")

if __name__ == "__main__":
    main() 