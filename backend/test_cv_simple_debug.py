#!/usr/bin/env python3
"""
Script simple para debuggear el flujo de datos del CV
"""

import json
import sys
import os

# Simular las funciones que necesitamos
def format_cv_analysis(cv_data: dict) -> str:
    """Formatea el análisis del CV de manera legible para la IA"""
    if not cv_data:
        return "No se proporcionó análisis de CV"
    
    # Verificar si cv_data es un diccionario válido
    if not isinstance(cv_data, dict):
        return "Formato de análisis de CV inválido"
    
    formatted = []
    
    # Siempre incluir información disponible, incluso si está incompleta
    if cv_data.get('strengths'):
        formatted.append("PUNTOS FUERTES:")
        for strength in cv_data['strengths']:
            formatted.append(f"  • {strength}")
        formatted.append("")
    elif cv_data.get('experience'):
        formatted.append("EXPERIENCIA LABORAL:")
        formatted.append(f"  • {cv_data['experience']}")
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
        formatted.append("")
    
    if cv_data.get('coherence'):
        formatted.append(f"COHERENCIA: {cv_data['coherence']}")
        formatted.append("")
    
    if cv_data.get('experience'):
        formatted.append(f"EXPERIENCIA LABORAL: {cv_data['experience']}")
        formatted.append("")
    
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
    
    # Si no hay datos estructurados pero hay texto raw, incluirlo
    if not formatted and cv_data.get('raw_text'):
        formatted.append("CONTENIDO DEL CV:")
        formatted.append(cv_data['raw_text'][:1000] + "..." if len(cv_data['raw_text']) > 1000 else cv_data['raw_text'])
        formatted.append("")
    
    # Si no hay ningún dato estructurado, intentar extraer información básica
    if not formatted:
        # Buscar cualquier campo que contenga información
        for key, value in cv_data.items():
            if value and key not in ['raw_text', 'analysis']:
                if isinstance(value, list) and value:
                    formatted.append(f"{key.upper()}:")
                    for item in value[:5]:  # Limitar a 5 elementos
                        formatted.append(f"  • {item}")
                    formatted.append("")
                elif isinstance(value, str) and value.strip():
                    formatted.append(f"{key.upper()}: {value}")
                    formatted.append("")
    
    return "\n".join(formatted) if formatted else "Análisis de CV disponible pero sin detalles específicos. Se realizará la evaluación basada en las habilidades soft evaluadas."

def test_cv_analysis():
    """Prueba el análisis de CV y la generación del informe"""
    
    print("🔍 Iniciando prueba de análisis de CV...")
    
    # Simular datos de CV (ejemplo básico)
    test_cv_data = {
        "strengths": ["Experiencia en desarrollo web", "Conocimiento de Python", "Trabajo en equipo"],
        "weaknesses": ["Falta de experiencia en gestión de proyectos", "Pocos proyectos de IA"],
        "feedback": "CV bien estructurado con experiencia relevante en desarrollo",
        "structure": "Clara y fácil de seguir",
        "coherence": "La experiencia es coherente con los objetivos profesionales",
        "experience": "3 años como desarrollador frontend en empresa tecnológica",
        "skills": ["JavaScript", "React", "Python", "Git"],
        "education": ["Ingeniería Informática - Universidad XYZ", "Curso de React - Platzi"],
        "alerts": ["Falta información de contacto", "Periodo de 6 meses sin actividad no explicado"]
    }
    
    print("\n📋 Datos de CV de prueba:")
    print(json.dumps(test_cv_data, indent=2, ensure_ascii=False))
    
    # Probar format_cv_analysis
    print("\n🔧 Probando format_cv_analysis...")
    formatted_cv = format_cv_analysis(test_cv_data)
    print("Resultado de format_cv_analysis:")
    print(formatted_cv)
    
    # Simular perfil completo
    perfil_completo = {
        "datos_personales": {
            "nombre": "Juan Pérez",
            "user_id": "test_user_123"
        },
        "habilidades_soft": [
            {
                "habilidad": "Comunicación",
                "puntuacion": 85,
                "nivel": "alto",
                "confianza": 90
            },
            {
                "habilidad": "Trabajo en equipo",
                "puntuacion": 75,
                "nivel": "medio",
                "confianza": 80
            }
        ],
        "analisis_cv": test_cv_data,
        "preferencias_laborales": {
            "areas": ["Desarrollo web", "Tecnología"],
            "needs": ["Flexibilidad horaria", "Trabajo remoto"],
            "workMode": "remoto",
            "availability": "completa"
        },
        "juegos_completados": ["juego1", "juego2"],
        "logs_juegos": []
    }
    
    # Construir perfil_texto como en main.py
    perfil_texto = f"""
PERFIL COMPLETO DEL CANDIDATO:

DATOS PERSONALES:
- Nombre: {perfil_completo['datos_personales']['nombre']}
- ID: {perfil_completo['datos_personales']['user_id']}

HABILIDADES SOFT EVALUADAS:
{chr(10).join([f"- {h['habilidad']}: {h['puntuacion']}% (Nivel: {h['nivel']}, Confianza: {h['confianza']}%)" for h in perfil_completo['habilidades_soft']])}

ANÁLISIS DETALLADO DEL CV:
{format_cv_analysis(perfil_completo['analisis_cv'])}

PREFERENCIAS LABORALES:
ÁREAS DE INTERÉS:
  • Desarrollo web
  • Tecnología

NECESIDADES ESPECÍFICAS:
  • Flexibilidad horaria
  • Trabajo remoto

MODO DE TRABAJO: remoto
DISPONIBILIDAD: completa

JUEGOS COMPLETADOS:
juego1, juego2

LOGS DE JUEGOS:
[]
"""
    
    print("\n📄 Perfil completo generado:")
    print(perfil_texto)
    
    # Verificar si el perfil incluye datos del CV
    cv_keywords = ["experiencia", "formación", "habilidades", "técnicas", "desarrollo", "python", "javascript", "puntos fuertes", "áreas de mejora"]
    found_keywords = [kw for kw in cv_keywords if kw.lower() in perfil_texto.lower()]
    
    print(f"\n🔍 Verificación de datos del CV en el perfil:")
    print(f"Palabras clave del CV encontradas: {found_keywords}")
    
    if found_keywords:
        print("✅ El perfil SÍ incluye datos del CV")
    else:
        print("❌ El perfil NO incluye datos del CV")

def test_empty_cv():
    """Prueba con CV vacío"""
    print("\n🔍 Probando con CV vacío...")
    
    empty_cv_data = {}
    formatted_empty = format_cv_analysis(empty_cv_data)
    print("Resultado con CV vacío:")
    print(formatted_empty)

def test_partial_cv():
    """Prueba con CV parcial"""
    print("\n🔍 Probando con CV parcial...")
    
    partial_cv_data = {
        "experience": "2 años como desarrollador",
        "skills": ["JavaScript", "React"],
        "education": ["Ingeniería Informática"]
    }
    
    formatted_partial = format_cv_analysis(partial_cv_data)
    print("Resultado con CV parcial:")
    print(formatted_partial)

def test_error_cv():
    """Prueba con CV que tiene errores"""
    print("\n🔍 Probando con CV con errores...")
    
    error_cv_data = {
        "error": "No se pudo analizar completamente el CV debido a errores en el análisis",
        "raw_text": "Juan Pérez\nDesarrollador\nJavaScript, React"
    }
    
    formatted_error = format_cv_analysis(error_cv_data)
    print("Resultado con CV con errores:")
    print(formatted_error)

if __name__ == "__main__":
    print("🚀 Iniciando pruebas de debug de CV...")
    
    test_cv_analysis()
    test_empty_cv()
    test_partial_cv()
    test_error_cv()
    
    print("\n✅ Pruebas completadas") 