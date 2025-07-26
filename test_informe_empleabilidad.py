#!/usr/bin/env python3
"""
Test específico para mostrar el informe de empleabilidad completo
"""

import requests
import json
from datetime import datetime

BACKEND_URL = "http://localhost:8000"

def mostrar_informe_empleabilidad():
    """Genera y muestra un informe de empleabilidad completo"""
    
    print("🎯 GENERANDO INFORME DE EMPLEABILIDAD COMPLETO")
    print("=" * 60)
    
    # Datos completos para el informe
    datos_usuario = {
        "userId": "demo-user-001",
        "fullName": "María García López",
        "softSkills": [
            {"skill": "Toma de decisiones", "level": "Alto", "confidence": 0.85, "score": 85},
            {"skill": "Resolución de problemas", "level": "Medio", "confidence": 0.65, "score": 65},
            {"skill": "Gestión emocional", "level": "Bajo", "confidence": 0.45, "score": 45},
            {"skill": "Comunicación", "level": "Alto", "confidence": 0.80, "score": 80},
            {"skill": "Trabajo en equipo", "level": "Medio", "confidence": 0.70, "score": 70},
            {"skill": "Liderazgo", "level": "Bajo", "confidence": 0.35, "score": 35}
        ],
        "cvAnalysis": {
            "strengths": [
                "Experiencia sólida en desarrollo frontend (5 años)",
                "Formación académica relevante (Ingeniería Informática)",
                "Certificaciones técnicas actualizadas (AWS, React)",
                "Conocimiento de tecnologías modernas (React, TypeScript)",
                "Experiencia en metodologías ágiles"
            ],
            "weaknesses": [
                "Falta experiencia en gestión de equipos grandes",
                "Necesita mejorar habilidades de presentación pública",
                "Poca experiencia en proyectos internacionales",
                "Falta de experiencia en arquitectura de sistemas"
            ],
            "feedback": "CV bien estructurado con buena experiencia técnica. El perfil muestra un desarrollador frontend competente con sólidos conocimientos técnicos. Áreas de mejora en liderazgo y comunicación pública.",
            "structure": "Clara y profesional, fácil de seguir",
            "coherence": "La experiencia es coherente con los objetivos profesionales",
            "experience": "5 años en desarrollo frontend con tecnologías modernas",
            "skills": ["React", "TypeScript", "JavaScript", "HTML5", "CSS3", "Git", "Jest", "Cypress"],
            "education": ["Ingeniería Informática", "Certificaciones AWS y React"],
            "alerts": ["Considerar agregar más detalles sobre logros específicos y métricas de impacto"]
        },
        "jobPreferences": {
            "areas": ["Desarrollo Frontend", "Desarrollo Web", "Tecnología"],
            "needs": ["Horario flexible", "Trabajo remoto", "Entorno colaborativo"],
            "workMode": "remoto",
            "availability": "completa",
            "willingToRelocate": False,
            "hasDisabilityCert": False
        },
        "completedGames": [1, 2, 3, 4, 5],
        "logs": [
            {
                "sceneId": 1,
                "decisions": [{"skill": "Toma de decisiones", "level": "Alto", "confidence": 0.85}],
                "totalSteps": 5,
                "totalTime": 180,
                "averageConfidence": 0.75,
                "emotionalTrend": ["positivo", "confiado"],
                "accessibilityUsed": False
            },
            {
                "sceneId": 2,
                "decisions": [{"skill": "Comunicación", "level": "Alto", "confidence": 0.80}],
                "totalSteps": 4,
                "totalTime": 150,
                "averageConfidence": 0.80,
                "emotionalTrend": ["positivo"],
                "accessibilityUsed": False
            }
        ]
    }
    
    try:
        print("📊 Enviando datos para generar informe...")
        response = requests.post(f"{BACKEND_URL}/api/logs/report", json=datos_usuario)
        
        if response.status_code == 200:
            informe = response.json()
            
            print("\n" + "="*60)
            print("📋 INFORME DE EMPLEABILIDAD GENERADO")
            print("="*60)
            
            # Información básica
            print(f"\n👤 USUARIO: {informe.get('report', {}).get('fullName', 'N/A')}")
            print(f"🆔 ID: {informe.get('report', {}).get('userId', 'N/A')}")
            print(f"📅 Fecha: {informe.get('createdAt', 'N/A')}")
            
            # Puntuación y nivel
            print(f"\n🎯 PUNTUACIÓN DE EMPLEABILIDAD: {informe.get('employabilityScore', 'N/A')}/100")
            print(f"📊 NIVEL: {informe.get('level', 'N/A')}")
            
            # Resumen
            print(f"\n📝 RESUMEN: {informe.get('summary', 'N/A')}")
            
            # Habilidades blandas evaluadas
            print(f"\n🧠 HABILIDADES BLANDAS EVALUADAS:")
            soft_skills = informe.get('report', {}).get('softSkills', [])
            for skill in soft_skills:
                nivel_emoji = "🟢" if skill.get('level') == 'Alto' else "🟡" if skill.get('level') == 'Medio' else "🔴"
                print(f"   {nivel_emoji} {skill.get('skill')}: {skill.get('level')} (Confianza: {skill.get('confidence', 0)*100:.0f}%)")
            
            # Análisis del CV
            cv_analysis = informe.get('report', {}).get('cvAnalysis', {})
            if cv_analysis:
                print(f"\n📄 ANÁLISIS DEL CV:")
                print(f"   ✅ Fortalezas: {len(cv_analysis.get('strengths', []))} detectadas")
                print(f"   ⚠️ Áreas de mejora: {len(cv_analysis.get('weaknesses', []))} identificadas")
                print(f"   💻 Habilidades técnicas: {', '.join(cv_analysis.get('skills', [])[:5])}")
                print(f"   🎓 Formación: {', '.join(cv_analysis.get('education', [])[:3])}")
            
            # Recomendaciones
            recommendations = informe.get('recommendations', {})
            if recommendations:
                print(f"\n💡 RECOMENDACIONES:")
                
                roles = recommendations.get('roles', [])
                if roles:
                    print(f"   💼 Roles sugeridos: {', '.join(roles)}")
                
                resources = recommendations.get('resources', [])
                if resources:
                    print(f"   📚 Recursos de formación: {', '.join(resources)}")
                
                improvements = recommendations.get('cvImprovements', [])
                if improvements:
                    print(f"   📝 Mejoras del CV: {', '.join(improvements[:3])}")
                
                next_steps = recommendations.get('nextSteps', [])
                if next_steps:
                    print(f"   🚀 Próximos pasos: {', '.join(next_steps[:3])}")
            
            # Preferencias laborales
            job_prefs = informe.get('report', {}).get('jobPreferences', {})
            if job_prefs:
                print(f"\n🎯 PREFERENCIAS LABORALES:")
                print(f"   📍 Áreas de interés: {', '.join(job_prefs.get('areas', []))}")
                print(f"   🏢 Modalidad: {job_prefs.get('workMode', 'N/A')}")
                print(f"   ⏰ Disponibilidad: {job_prefs.get('availability', 'N/A')}")
                print(f"   🚚 ¿Mudarse?: {'Sí' if job_prefs.get('willingToRelocate') else 'No'}")
            
            # Juegos completados
            completed_games = informe.get('report', {}).get('completedGames', [])
            if completed_games:
                print(f"\n🎮 MINIJUEGOS COMPLETADOS: {len(completed_games)}")
                print(f"   🎯 Juegos: {', '.join(map(str, completed_games))}")
            
            # Métricas adicionales
            print(f"\n📈 MÉTRICAS ADICIONALES:")
            print(f"   🎯 Habilidades altas: {len([s for s in soft_skills if s.get('level') == 'Alto'])}")
            print(f"   🎯 Habilidades medias: {len([s for s in soft_skills if s.get('level') == 'Medio'])}")
            print(f"   🎯 Habilidades bajas: {len([s for s in soft_skills if s.get('level') == 'Bajo'])}")
            
            # Calificación final
            score = informe.get('employabilityScore', 0)
            if score >= 80:
                calificacion = "🟢 EXCELENTE"
            elif score >= 60:
                calificacion = "🟡 BUENA"
            else:
                calificacion = "🔴 MEJORABLE"
            
            print(f"\n🏆 CALIFICACIÓN FINAL: {calificacion}")
            
            print("\n" + "="*60)
            print("✅ INFORME COMPLETADO EXITOSAMENTE")
            print("="*60)
            
            return True
            
        else:
            print(f"❌ Error generando informe: {response.status_code}")
            print(f"Respuesta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error en la generación: {str(e)}")
        return False

if __name__ == "__main__":
    mostrar_informe_empleabilidad() 