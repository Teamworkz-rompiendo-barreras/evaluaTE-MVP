#!/usr/bin/env python3
"""
Script completo para probar el análisis de CV real con cv_prueba.pdf
Incluye extracción de texto, análisis del CV y generación del informe completo
"""

import os
import json
import sys
from datetime import datetime
from pathlib import Path

# Agregar el directorio actual al path para importar módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from cv_analyzer import extract_pdf_info
from generate_report import generar_informe

def test_analisis_cv_completo():
    """
    Prueba completa del análisis de CV real
    """
    print("🔍 PRUEBA COMPLETA DE ANÁLISIS DE CV REAL")
    print("=" * 60)
    
    # Verificar que el archivo existe
    cv_path = "cv_prueba.pdf"
    if not os.path.exists(cv_path):
        print(f"❌ Error: No se encuentra el archivo {cv_path}")
        return
    
    print(f"✅ Archivo encontrado: {cv_path}")
    print(f"📊 Tamaño: {os.path.getsize(cv_path)} bytes")
    print()
    
    try:
        # Paso 1: Leer el archivo PDF
        print("📖 PASO 1: Leyendo archivo PDF...")
        with open(cv_path, 'rb') as f:
            pdf_buffer = f.read()
        
        print(f"✅ PDF leído: {len(pdf_buffer)} bytes")
        print()
        
        # Paso 2: Extraer información del PDF
        print("🔍 PASO 2: Extrayendo información del PDF...")
        cv_data = extract_pdf_info(pdf_buffer)
        
        if not cv_data:
            print("❌ Error: No se pudo extraer información del PDF")
            return
        
        print("✅ Información extraída exitosamente")
        print()
        
        # Paso 3: Mostrar información extraída
        print("📋 PASO 3: Información extraída del CV:")
        print("-" * 40)
        
        # Información de contacto
        if cv_data.get('contact'):
            print("📧 INFORMACIÓN DE CONTACTO:")
            for key, value in cv_data['contact'].items():
                print(f"  {key}: {value}")
            print()
        
        # Habilidades detectadas
        if cv_data.get('skills'):
            print("🛠️ HABILIDADES DETECTADAS:")
            for skill in cv_data['skills']:
                print(f"  • {skill}")
            print()
        
        # Experiencia laboral
        if cv_data.get('experience'):
            print("💼 EXPERIENCIA LABORAL:")
            for exp in cv_data['experience']:
                print(f"  • {exp.get('title', 'N/A')} en {exp.get('company', 'N/A')}")
                if exp.get('duration'):
                    print(f"    Duración: {exp['duration']}")
                if exp.get('description'):
                    print(f"    Descripción: {exp['description'][:100]}...")
            print()
        
        # Educación
        if cv_data.get('education'):
            print("🎓 FORMACIÓN ACADÉMICA:")
            for edu in cv_data['education']:
                print(f"  • {edu.get('degree', 'N/A')} - {edu.get('institution', 'N/A')}")
                if edu.get('year'):
                    print(f"    Año: {edu['year']}")
            print()
        
        # Análisis del CV
        if cv_data.get('analysis'):
            print("📊 ANÁLISIS DEL CV:")
            analysis = cv_data['analysis']
            
            if analysis.get('strengths'):
                print("  ✅ PUNTOS FUERTES:")
                for strength in analysis['strengths']:
                    print(f"    • {strength}")
            
            if analysis.get('weaknesses'):
                print("  ⚠️ ÁREAS DE MEJORA:")
                for weakness in analysis['weaknesses']:
                    print(f"    • {weakness}")
            
            if analysis.get('feedback'):
                print(f"  💡 FEEDBACK: {analysis['feedback']}")
            
            if analysis.get('structure'):
                print(f"  📐 ESTRUCTURA: {analysis['structure']}")
            
            if analysis.get('coherence'):
                print(f"  🔗 COHERENCIA: {analysis['coherence']}")
            
            if analysis.get('experience'):
                print(f"  💼 EXPERIENCIA: {analysis['experience']}")
            
            if analysis.get('alerts'):
                print("  🚨 ALERTAS:")
                for alert in analysis['alerts']:
                    print(f"    • {alert}")
            print()
        
        # Paso 4: Crear datos simulados para el informe completo
        print("🎮 PASO 4: Creando datos simulados para el informe completo...")
        
        # Datos simulados de soft skills (resultados de minijuegos)
        soft_skills = [
            {"skill": "Comunicación", "score": 85, "level": "alto", "confidence": 90},
            {"skill": "Trabajo en equipo", "score": 78, "level": "medio", "confidence": 85},
            {"skill": "Resolución de problemas", "score": 92, "level": "alto", "confidence": 95},
            {"skill": "Adaptabilidad", "score": 70, "level": "medio", "confidence": 80},
            {"skill": "Liderazgo", "score": 65, "level": "medio", "confidence": 75},
            {"skill": "Gestión del tiempo", "score": 88, "level": "alto", "confidence": 90}
        ]
        
        # Preferencias laborales simuladas
        job_preferences = {
            "areas": ["Desarrollo de software", "Análisis de datos", "Gestión de proyectos"],
            "needs": ["Flexibilidad horaria", "Trabajo remoto", "Entorno inclusivo"],
            "workMode": "híbrido",
            "availability": "completa",
            "willingToRelocate": True,
            "hasDisabilityCert": False
        }
        
        # Configuración de accesibilidad
        accessibility = {
            "easyReadingMode": False,
            "audioAssistiveMode": False,
            "showPictograms": False,
            "contrastLevel": "normal"
        }
        
        print("✅ Datos simulados creados")
        print()
        
        # Paso 5: Formatear el perfil completo para la IA
        print("📝 PASO 5: Formateando perfil completo para análisis de IA...")
        
        # Formatear información del CV
        cv_info = f"""
INFORMACIÓN DEL CV ANALIZADO:

CONTACTO:
{json.dumps(cv_data.get('contact', {}), indent=2, ensure_ascii=False)}

HABILIDADES TÉCNICAS DETECTADAS:
{chr(10).join([f"• {skill}" for skill in cv_data.get('skills', [])])}

EXPERIENCIA LABORAL:
{chr(10).join([f"• {exp.get('title', 'N/A')} en {exp.get('company', 'N/A')} ({exp.get('duration', 'N/A')})" for exp in cv_data.get('experience', [])])}

FORMACIÓN ACADÉMICA:
{chr(10).join([f"• {edu.get('degree', 'N/A')} - {edu.get('institution', 'N/A')} ({edu.get('year', 'N/A')})" for edu in cv_data.get('education', [])])}

ANÁLISIS DEL CV:
{json.dumps(cv_data.get('analysis', {}), indent=2, ensure_ascii=False)}
"""
        
        # Formatear soft skills
        soft_skills_info = f"""
RESULTADOS DE EVALUACIÓN DE SOFT SKILLS:

{chr(10).join([f"• {skill['skill']}: {skill['score']}/100 ({skill['level']}) - Confianza: {skill['confidence']}%" for skill in soft_skills])}

INTERPRETACIÓN DE RESULTADOS:
- Comunicación: Excelente capacidad de expresión y escucha activa
- Trabajo en equipo: Buena colaboración, con espacio para mejora en liderazgo
- Resolución de problemas: Fortaleza destacada en análisis y solución creativa
- Adaptabilidad: Capacidad moderada para cambios, requiere apoyo en transiciones
- Liderazgo: Potencial de desarrollo en roles de supervisión
- Gestión del tiempo: Excelente organización y cumplimiento de plazos
"""
        
        # Formatear preferencias laborales
        preferences_info = f"""
PREFERENCIAS LABORALES:

ÁREAS DE INTERÉS:
{chr(10).join([f"• {area}" for area in job_preferences['areas']])}

NECESIDADES ESPECÍFICAS:
{chr(10).join([f"• {need}" for need in job_preferences['needs']])}

CONFIGURACIÓN LABORAL:
• Modo de trabajo: {job_preferences['workMode']}
• Disponibilidad: {job_preferences['availability']}
• Disposición a reubicación: {'Sí' if job_preferences['willingToRelocate'] else 'No'}
• Certificado de discapacidad: {'Sí' if job_preferences['hasDisabilityCert'] else 'No'}

CONFIGURACIÓN DE ACCESIBILIDAD:
• Modo lectura fácil: {'Activado' if accessibility['easyReadingMode'] else 'Desactivado'}
• Asistencia de audio: {'Activado' if accessibility['audioAssistiveMode'] else 'Desactivado'}
• Pictogramas: {'Activado' if accessibility['showPictograms'] else 'Desactivado'}
• Nivel de contraste: {accessibility['contrastLevel']}
"""
        
        # Perfil completo
        perfil_completo = f"""
DATOS DEL CANDIDATO:
Nombre: Usuario de Prueba
Fecha de análisis: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}

{cv_info}

{soft_skills_info}

{preferences_info}
"""
        
        print("✅ Perfil completo formateado")
        print()
        
        # Paso 6: Generar informe completo
        print("🤖 PASO 6: Generando informe completo con IA...")
        print("⏳ Esto puede tomar varios minutos...")
        
        try:
            informe = generar_informe(perfil_completo)
            
            print("✅ Informe generado exitosamente!")
            print()
            
            # Paso 7: Guardar el informe
            print("💾 PASO 7: Guardando informe...")
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            informe_filename = f"informe_cv_prueba_{timestamp}.md"
            
            with open(informe_filename, 'w', encoding='utf-8') as f:
                f.write(f"# INFORME DE EMPLEABILIDAD NEUROINCLUSIVA\n\n")
                f.write(f"**Fecha de generación:** {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
                f.write(f"**Archivo analizado:** {cv_path}\n\n")
                f.write("---\n\n")
                f.write(informe)
            
            print(f"✅ Informe guardado como: {informe_filename}")
            print()
            
            # Paso 8: Mostrar resumen del informe
            print("📊 PASO 8: Resumen del informe generado:")
            print("-" * 40)
            
            # Contar palabras y secciones
            palabras = len(informe.split())
            lineas = len(informe.split('\n'))
            
            print(f"📝 Longitud del informe:")
            print(f"  • Palabras: {palabras:,}")
            print(f"  • Líneas: {lineas:,}")
            print(f"  • Caracteres: {len(informe):,}")
            print()
            
            # Mostrar las primeras líneas del informe
            print("📖 Vista previa del informe:")
            print("-" * 40)
            lineas_preview = informe.split('\n')[:20]
            for linea in lineas_preview:
                print(linea)
            
            if len(informe.split('\n')) > 20:
                print("...")
                lineas_totales = len(informe.split('\n'))
                print(f"(Mostrando 20 de {lineas_totales} líneas)")
            
            print()
            print("🎉 ¡PRUEBA COMPLETADA EXITOSAMENTE!")
            print(f"📄 El informe completo está disponible en: {informe_filename}")
            
        except Exception as e:
            print(f"❌ Error generando el informe: {e}")
            print("💡 Verifica que las variables de entorno de Azure OpenAI estén configuradas correctamente")
    
    except Exception as e:
        print(f"❌ Error durante el análisis: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_analisis_cv_completo() 