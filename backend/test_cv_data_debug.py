#!/usr/bin/env python3
"""
Script para debuggear el flujo de datos del CV
"""

import json
import sys
import os
from pathlib import Path

# Añadir el directorio actual al path para importar módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from cv_analyzer import extract_pdf_info
from main import format_cv_analysis, generar_informe

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
    
    # Probar generación de informe
    print("\n🤖 Generando informe de prueba...")
    try:
        informe = generar_informe(perfil_texto)
        print("✅ Informe generado exitosamente")
        print("\n📊 Informe generado:")
        print(informe)
        
        # Verificar si el informe incluye datos del CV
        cv_keywords = ["experiencia", "formación", "habilidades", "técnicas", "desarrollo", "python", "javascript"]
        found_keywords = [kw for kw in cv_keywords if kw.lower() in informe.lower()]
        
        print(f"\n🔍 Verificación de datos del CV en el informe:")
        print(f"Palabras clave del CV encontradas: {found_keywords}")
        
        if found_keywords:
            print("✅ El informe SÍ incluye datos del CV")
        else:
            print("❌ El informe NO incluye datos del CV")
            
    except Exception as e:
        print(f"❌ Error generando informe: {str(e)}")
        import traceback
        print(f"📋 Traceback: {traceback.format_exc()}")

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

if __name__ == "__main__":
    print("🚀 Iniciando pruebas de debug de CV...")
    
    test_cv_analysis()
    test_empty_cv()
    test_partial_cv()
    
    print("\n✅ Pruebas completadas") 