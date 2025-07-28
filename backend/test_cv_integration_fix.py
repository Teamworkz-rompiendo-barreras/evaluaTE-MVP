#!/usr/bin/env python3
"""
Script para probar la integración de datos del CV en el informe
"""

import json
import sys
import os

# Simular las funciones que necesitamos
def extract_basic_cv_info(text: str) -> dict:
    """Extrae información básica del texto del CV cuando no hay datos estructurados"""
    info = {
        "strengths": [],
        "weaknesses": [],
        "feedback": "Análisis básico del CV basado en el texto extraído",
        "structure": "Información extraída del CV",
        "coherence": "Datos disponibles del CV",
        "experience": "",
        "skills": [],
        "education": [],
        "alerts": []
    }
    
    # Buscar patrones básicos en el texto
    lines = text.split('\n')
    
    # Buscar habilidades técnicas comunes
    tech_keywords = [
        "javascript", "python", "java", "c++", "c#", "php", "ruby", "go", "rust",
        "react", "angular", "vue", "node.js", "express", "django", "flask",
        "sql", "mysql", "postgresql", "mongodb", "redis",
        "html", "css", "bootstrap", "tailwind", "sass", "less",
        "git", "docker", "kubernetes", "aws", "azure", "gcp",
        "machine learning", "ai", "data science", "analytics"
    ]
    
    found_skills = []
    for line in lines:
        line_lower = line.lower()
        for keyword in tech_keywords:
            if keyword in line_lower:
                found_skills.append(keyword.title())
    
    info["skills"] = list(set(found_skills))  # Eliminar duplicados
    
    # Buscar formación académica
    education_keywords = ["universidad", "universidad", "grado", "licenciatura", "ingeniería", "master", "máster", "doctorado", "curso", "certificación"]
    found_education = []
    for line in lines:
        line_lower = line.lower()
        for keyword in education_keywords:
            if keyword in line_lower:
                found_education.append(line.strip())
    
    info["education"] = found_education[:5]  # Limitar a 5 elementos
    
    # Buscar experiencia laboral
    experience_keywords = ["años", "experiencia", "desarrollador", "programador", "analista", "ingeniero", "consultor"]
    for line in lines:
        line_lower = line.lower()
        if any(keyword in line_lower for keyword in experience_keywords):
            info["experience"] = line.strip()
            break
    
    # Si no se encontró experiencia específica, usar el texto completo como experiencia
    if not info["experience"] and text.strip():
        info["experience"] = text[:200] + "..." if len(text) > 200 else text
    
    return info

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

def test_cv_error_scenario():
    """Prueba el escenario donde hay errores en el análisis del CV"""
    
    print("🔍 Probando escenario con errores en análisis de CV...")
    
    # Simular texto extraído del CV
    cv_text = """
    Juan Pérez
    Desarrollador Frontend
    
    EXPERIENCIA:
    - 3 años como desarrollador frontend en TechCorp
    - 2 años como programador en StartupXYZ
    
    HABILIDADES:
    - JavaScript, React, TypeScript
    - HTML, CSS, Bootstrap
    - Git, Docker
    
    FORMACIÓN:
    - Ingeniería Informática - Universidad de Madrid
    - Curso de React - Platzi
    
    PROYECTOS:
    - E-commerce con React y Node.js
    - Dashboard administrativo con TypeScript
    """
    
    print(f"\n📋 Texto del CV extraído:")
    print(cv_text)
    
    # Simular que el análisis estructurado falló pero tenemos el texto
    cv_analysis = {
        "error": "No se pudo analizar completamente el CV debido a errores en el análisis",
        "raw_text": cv_text
    }
    
    print(f"\n❌ Análisis estructurado falló:")
    print(json.dumps(cv_analysis, indent=2, ensure_ascii=False))
    
    # Extraer información básica del texto
    basic_info = extract_basic_cv_info(cv_text)
    print(f"\n🔧 Información básica extraída:")
    print(json.dumps(basic_info, indent=2, ensure_ascii=False))
    
    # Formatear para el informe
    formatted_cv = format_cv_analysis(basic_info)
    print(f"\n📄 CV formateado para el informe:")
    print(formatted_cv)
    
    # Verificar si incluye datos reales del CV
    cv_keywords = ["javascript", "react", "typescript", "html", "css", "git", "docker", "ingeniería", "universidad", "desarrollador", "frontend"]
    found_keywords = [kw for kw in cv_keywords if kw.lower() in formatted_cv.lower()]
    
    print(f"\n🔍 Verificación de datos del CV:")
    print(f"Palabras clave del CV encontradas: {found_keywords}")
    
    if found_keywords:
        print("✅ El CV formateado SÍ incluye datos reales del CV")
    else:
        print("❌ El CV formateado NO incluye datos reales del CV")

def test_empty_cv_with_text():
    """Prueba con CV vacío pero con texto extraído"""
    print("\n🔍 Probando con CV vacío pero con texto...")
    
    cv_text = "María García\nDesarrolladora\nPython, Django, PostgreSQL"
    
    # Simular CV vacío pero con texto
    empty_cv_data = {
        "raw_text": cv_text
    }
    
    # Extraer información básica
    basic_info = extract_basic_cv_info(cv_text)
    formatted_cv = format_cv_analysis(basic_info)
    
    print("Resultado con CV vacío pero con texto:")
    print(formatted_cv)
    
    # Verificar si incluye datos reales
    cv_keywords = ["python", "django", "postgresql", "maría", "garcía", "desarrolladora"]
    found_keywords = [kw for kw in cv_keywords if kw.lower() in formatted_cv.lower()]
    
    print(f"Palabras clave encontradas: {found_keywords}")
    
    if found_keywords:
        print("✅ Incluye datos reales del CV")
    else:
        print("❌ No incluye datos reales del CV")

if __name__ == "__main__":
    print("🚀 Iniciando pruebas de integración de CV...")
    
    test_cv_error_scenario()
    test_empty_cv_with_text()
    
    print("\n✅ Pruebas completadas") 