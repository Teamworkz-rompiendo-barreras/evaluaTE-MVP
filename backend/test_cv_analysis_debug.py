#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de debug para verificar el análisis del CV y su inclusión en el informe final
"""

import json
import sys
import os
from pathlib import Path

# Agregar el directorio actual al path para importar módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_cv_analysis():
    """Prueba el análisis del CV usando cv_analyzer"""
    print("🔍 PRUEBA DE ANÁLISIS DE CV")
    print("=" * 50)
    
    try:
        from cv_analyzer import extract_pdf_info
        
        # Usar el CV de prueba
        cv_path = "cv_prueba.pdf"
        if not os.path.exists(cv_path):
            print(f"❌ No se encuentra el archivo {cv_path}")
            return False
        
        print(f"📄 Analizando CV: {cv_path}")
        
        # Leer el archivo PDF
        with open(cv_path, 'rb') as f:
            pdf_content = f.read()
        
        # Analizar el CV
        result = extract_pdf_info(pdf_content)
        
        if result.get("error"):
            print(f"❌ Error en análisis: {result['error']}")
            return False
        
        print("✅ Análisis completado")
        print(f"📝 Texto extraído: {len(result.get('raw_text', ''))} caracteres")
        
        # Mostrar detalles del análisis
        analysis = result.get('analysis', {})
        print("\n📊 RESULTADOS DEL ANÁLISIS:")
        print(f"  • Fortalezas: {len(analysis.get('strengths', []))}")
        print(f"  • Debilidades: {len(analysis.get('weaknesses', []))}")
        print(f"  • Habilidades: {len(analysis.get('skills', []))}")
        print(f"  • Educación: {len(analysis.get('education', []))}")
        print(f"  • Alertas: {len(analysis.get('alerts', []))}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_informe_generation():
    """Prueba la generación del informe con datos del CV"""
    print("\n📋 PRUEBA DE GENERACIÓN DE INFORME")
    print("=" * 50)
    
    try:
        from main import EmployabilityReportRequest, SoftSkillResult, CvAnalysis
        from generate_report import generar_informe
        
        # Crear datos de prueba
        test_cv_analysis = CvAnalysis(
            strengths=["Experiencia en desarrollo web", "Conocimientos de Python"],
            weaknesses=["Falta de experiencia en gestión de proyectos"],
            feedback="CV bien estructurado pero necesita más detalles en proyectos",
            structure="Clara y fácil de seguir",
            coherence="La experiencia es coherente con los objetivos",
            experience="3 años en desarrollo web",
            skills=["Python", "JavaScript", "React", "Django"],
            education=["Ingeniería Informática", "Curso de Desarrollo Web"],
            alerts=["Falta información de contacto", "Periodos sin actividad no explicados"]
        )
        
        test_soft_skills = [
            SoftSkillResult(skill="Comunicación", score=75, level="medio", confidence=80),
            SoftSkillResult(skill="Trabajo en equipo", score=85, level="alto", confidence=90),
            SoftSkillResult(skill="Resolución de problemas", score=70, level="medio", confidence=75)
        ]
        
        # Crear request de prueba
        test_request = EmployabilityReportRequest(
            userId="test_user",
            fullName="Ana García",
            softSkills=test_soft_skills,
            cvAnalysis=test_cv_analysis,
            jobPreferences=None,
            completedGames=[],
            logs=[]
        )
        
        print("📝 Generando informe con datos del CV...")
        
        # Preparar perfil para la IA
        perfil_texto = f"""
PERFIL COMPLETO DEL CANDIDATO:

DATOS PERSONALES:
- Nombre: {test_request.fullName}
- ID: {test_request.userId}

HABILIDADES SOFT EVALUADAS:
{chr(10).join([f"- {skill.skill}: {skill.score}% (Nivel: {skill.level}, Confianza: {skill.confidence}%)" for skill in test_request.softSkills])}

ANÁLISIS DETALLADO DEL CV:
{format_cv_analysis(test_request.cvAnalysis.dict()) if test_request.cvAnalysis else "No se proporcionó análisis de CV"}

PREFERENCIAS LABORALES:
No se especificaron preferencias laborales

JUEGOS COMPLETADOS:
Ningún juego completado

LOGS DE JUEGOS:
No hay logs de juegos disponibles
"""
        
        # Generar informe
        informe = generar_informe(perfil_texto)
        
        print("✅ Informe generado")
        print(f"📄 Longitud del informe: {len(informe)} caracteres")
        
        # Verificar si el CV se menciona en el informe
        cv_keywords = ["CV", "currículum", "experiencia", "habilidades técnicas", "formación"]
        cv_mentioned = any(keyword.lower() in informe.lower() for keyword in cv_keywords)
        
        print(f"🔍 CV mencionado en informe: {'✅ SÍ' if cv_mentioned else '❌ NO'}")
        
        # Mostrar fragmento del informe
        print("\n📄 FRAGMENTO DEL INFORME:")
        lines = informe.split('\n')
        for i, line in enumerate(lines[:20]):  # Primeras 20 líneas
            print(f"{i+1:2d}: {line}")
        
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

def test_pdf_generation():
    """Prueba la generación del PDF con datos del CV"""
    print("\n📄 PRUEBA DE GENERACIÓN DE PDF")
    print("=" * 50)
    
    try:
        from pdf_service import create_employability_pdf
        
        # Crear datos de prueba
        test_data = {
            "gameData": [
                {"subject": "Comunicación", "dA": 75, "level": "medio"},
                {"subject": "Trabajo en equipo", "dA": 85, "level": "alto"},
                {"subject": "Resolución de problemas", "dA": 70, "level": "medio"}
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
                "availability": "completa"
            },
            "userInfo": {
                "fullName": "Ana García",
                "userId": "test_user"
            },
            "informeProfesional": "Informe profesional de prueba generado por IA..."
        }
        
        print("📄 Generando PDF con datos del CV...")
        
        # Generar PDF
        pdf_content = create_employability_pdf(test_data)
        
        print("✅ PDF generado")
        print(f"📄 Tamaño del PDF: {len(pdf_content)} bytes")
        
        # Guardar PDF para verificación
        output_path = "test_informe_con_cv.pdf"
        with open(output_path, 'wb') as f:
            f.write(pdf_content)
        
        print(f"💾 PDF guardado como: {output_path}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Ejecuta todas las pruebas"""
    print("🚀 INICIANDO PRUEBAS DE DEBUG DEL CV")
    print("=" * 60)
    
    # Prueba 1: Análisis del CV
    test1_success = test_cv_analysis()
    
    # Prueba 2: Generación de informe
    test2_success = test_informe_generation()
    
    # Prueba 3: Generación de PDF
    test3_success = test_pdf_generation()
    
    # Resumen
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE PRUEBAS:")
    print(f"  • Análisis de CV: {'✅ EXITOSO' if test1_success else '❌ FALLIDO'}")
    print(f"  • Generación de informe: {'✅ EXITOSO' if test2_success else '❌ FALLIDO'}")
    print(f"  • Generación de PDF: {'✅ EXITOSO' if test3_success else '❌ FALLIDO'}")
    
    if all([test1_success, test2_success, test3_success]):
        print("\n🎉 TODAS LAS PRUEBAS EXITOSAS")
        print("💡 El análisis del CV está funcionando correctamente")
    else:
        print("\n⚠️ ALGUNAS PRUEBAS FALLARON")
        print("🔧 Revisar los errores anteriores")

if __name__ == "__main__":
    main() 