#!/usr/bin/env python3
"""
Script para debuggear los datos del CV que se pasan al informe
"""

import os
import sys
import json
import requests

# Agregar el directorio actual al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def debug_cv_data():
    """Debuggea los datos del CV que se pasan al informe"""
    
    print("🔍 DEBUGGEO DE DATOS DEL CV")
    print("=" * 50)
    
    try:
        # 1. Extraer datos del CV usando el módulo interno
        from cv_analyzer import extract_pdf_info
        
        # Leer el archivo PDF
        pdf_path = "curriculum_21.pdf"
        with open(pdf_path, 'rb') as f:
            pdf_buffer = f.read()
        
        print("🔍 Paso 1: Extrayendo datos del CV...")
        cv_result = extract_pdf_info(pdf_buffer)
        
        if cv_result.get('error'):
            print(f"❌ Error extrayendo CV: {cv_result['error']}")
            return False
        
        print("✅ Datos extraídos correctamente")
        
        # Mostrar los datos extraídos por Document Intelligence
        cv_info = cv_result.get('cv_info', {})
        print(f"\n📊 DATOS EXTRAÍDOS POR DOCUMENT INTELLIGENCE:")
        print("-" * 50)
        print(f"Contacto: {cv_info.get('contacto', {})}")
        print(f"Software: {cv_info.get('software', [])}")
        print(f"Idiomas: {cv_info.get('idiomas', [])}")
        print(f"Experiencia: {cv_info.get('experiencia', [])}")
        print(f"Educación: {cv_info.get('educacion', [])}")
        print(f"Habilidades: {cv_info.get('habilidades', [])}")
        print(f"Proyectos: {cv_info.get('proyectos', [])}")
        
        # 2. Llamar al endpoint de análisis de CV
        print(f"\n📤 Paso 2: Llamando al endpoint de análisis de CV...")
        
        test_data = {
            'userId': 'test_user_21',
            'fullName': 'ESTHER PÉREZ',
            'softSkills': json.dumps([
                {
                    'skill': 'Comunicación',
                    'score': 85,
                    'level': 'alto',
                    'confidence': 90
                },
                {
                    'skill': 'Trabajo en equipo',
                    'score': 75,
                    'level': 'medio',
                    'confidence': 85
                }
            ]),
            'jobPreferences': json.dumps({
                'areas': ['Diseño gráfico', 'Multimedia'],
                'needs': ['Flexibilidad horaria', 'Trabajo creativo'],
                'workMode': 'remoto',
                'availability': 'completa',
                'willingToRelocate': False,
                'hasDisabilityCert': False
            }),
            'completedGames': json.dumps(['memory_game', 'attention_test'])
        }
        
        # Llamar al endpoint de análisis de CV
        with open(pdf_path, 'rb') as f:
            files = {'file': (pdf_path, f, 'application/pdf')}
            response = requests.post(
                "http://localhost:8000/api/pdf/analyze-cv",
                files=files,
                data=test_data,
                timeout=60
            )
        
        if response.status_code != 200:
            print(f"❌ Error en análisis de CV: {response.status_code}")
            print(f"Respuesta: {response.text}")
            return False
        
        cv_analysis = response.json()
        print("✅ Análisis de CV completado")
        
        # Mostrar los datos del CvAnalysis
        print(f"\n📊 DATOS DEL CVANALYSIS:")
        print("-" * 30)
        print(f"Strengths: {cv_analysis.get('strengths', [])}")
        print(f"Weaknesses: {cv_analysis.get('weaknesses', [])}")
        print(f"Feedback: {cv_analysis.get('feedback', '')}")
        print(f"Structure: {cv_analysis.get('structure', '')}")
        print(f"Coherence: {cv_analysis.get('coherence', '')}")
        print(f"Experience: {cv_analysis.get('experience', '')}")
        print(f"Skills: {cv_analysis.get('skills', [])}")
        print(f"Education: {cv_analysis.get('education', [])}")
        print(f"Alerts: {cv_analysis.get('alerts', [])}")
        
        # 3. Simular el formateo que hace format_cv_analysis
        print(f"\n📝 SIMULANDO FORMAT_CV_ANALYSIS:")
        print("-" * 30)
        
        # Importar la función format_cv_analysis
        from main import format_cv_analysis
        
        formatted_cv = format_cv_analysis(cv_analysis)
        print("RESULTADO DE FORMAT_CV_ANALYSIS:")
        print(formatted_cv)
        
        # 4. Crear el perfil completo que se envía a la IA
        print(f"\n📋 PERFIL COMPLETO ENVIADO A LA IA:")
        print("-" * 40)
        
        perfil_texto = f"""
DATOS DEL CANDIDATO:
Nombre: ESTHER PÉREZ
ID de Usuario: test_user_21

HABILIDADES SOFT EVALUADAS:
- Comunicación: 90%
- Trabajo en equipo: 85%

ANÁLISIS DETALLADO DEL CV:
{formatted_cv}

PREFERENCIAS LABORALES:
ÁREAS DE INTERÉS:
  • Diseño gráfico
  • Multimedia

NECESIDADES ESPECÍFICAS:
  • Flexibilidad horaria
  • Trabajo creativo

MODALIDAD DE TRABAJO: Remoto
DISPONIBILIDAD: Completa

JUEGOS COMPLETADOS:
memory_game, attention_test

LOGS DE JUEGOS:
No se dispone de logs detallados de juegos. La evaluación se basa en los resultados de habilidades soft proporcionados.
"""
        
        print(perfil_texto)
        
        # 5. Verificar qué datos faltan
        print(f"\n🔍 ANÁLISIS DE DATOS FALTANTES:")
        print("-" * 30)
        
        missing_data = []
        
        # Verificar datos de contacto
        if not cv_analysis.get('strengths') or not any('email' in str(s).lower() for s in cv_analysis.get('strengths', [])):
            missing_data.append("Email de contacto")
        
        if not cv_analysis.get('strengths') or not any('teléfono' in str(s).lower() for s in cv_analysis.get('strengths', [])):
            missing_data.append("Teléfono de contacto")
        
        # Verificar idiomas
        if not cv_analysis.get('skills') or not any('español' in str(s).lower() or 'inglés' in str(s).lower() for s in cv_analysis.get('skills', [])):
            missing_data.append("Idiomas")
        
        # Verificar ubicación
        if not cv_analysis.get('strengths') or not any('parandones' in str(s).lower() or 'león' in str(s).lower() for s in cv_analysis.get('strengths', [])):
            missing_data.append("Ubicación")
        
        if missing_data:
            print(f"❌ DATOS FALTANTES EN CVANALYSIS:")
            for data in missing_data:
                print(f"  - {data}")
        else:
            print("✅ Todos los datos están presentes en CvAnalysis")
        
        print(f"\n💡 CONCLUSIÓN:")
        print("-" * 20)
        print("Los datos extraídos por Document Intelligence NO se están pasando")
        print("al modelo CvAnalysis, por lo que no llegan al informe final.")
        print("Necesitamos modificar el endpoint /api/pdf/analyze-cv para incluir")
        print("todos los datos extraídos en el CvAnalysis.")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    debug_cv_data() 