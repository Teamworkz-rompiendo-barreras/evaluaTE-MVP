#!/usr/bin/env python3
"""
Script de prueba para Azure AI Document Intelligence
Este script prueba la funcionalidad de Document Intelligence con un CV de ejemplo.
"""

import os
import sys
import tempfile
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def print_header(title):
    """Imprime un encabezado formateado"""
    print("\n" + "="*60)
    print(f"🧪 {title}")
    print("="*60)

def print_success(message):
    """Imprime un mensaje de éxito"""
    print(f"✅ {message}")

def print_error(message):
    """Imprime un mensaje de error"""
    print(f"❌ {message}")

def print_info(message):
    """Imprime un mensaje informativo"""
    print(f"ℹ️ {message}")

def create_test_cv_pdf():
    """Crea un PDF de prueba con contenido de CV"""
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib.units import inch
        from io import BytesIO
        
        # Crear buffer para el PDF
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []
        
        # Contenido del CV de prueba
        cv_content = [
            ("CURRICULUM VITAE", styles['Title']),
            ("", styles['Normal']),
            ("DATOS PERSONALES", styles['Heading2']),
            ("Nombre: Juan Carlos Pérez García", styles['Normal']),
            ("Email: juan.perez@email.com", styles['Normal']),
            ("Teléfono: +34 612 345 678", styles['Normal']),
            ("", styles['Normal']),
            ("EXPERIENCIA LABORAL", styles['Heading2']),
            ("Desarrollador Frontend Senior - TechCorp S.L.", styles['Normal']),
            ("2020 - 2023", styles['Normal']),
            ("• Desarrollo de aplicaciones web con React y TypeScript", styles['Normal']),
            ("• Optimización de rendimiento y SEO", styles['Normal']),
            ("• Liderazgo de equipo de 5 desarrolladores", styles['Normal']),
            ("", styles['Normal']),
            ("Desarrollador Web - StartupXYZ", styles['Normal']),
            ("2018 - 2020", styles['Normal']),
            ("• Desarrollo full-stack con Node.js y React", styles['Normal']),
            ("• Implementación de APIs RESTful", styles['Normal']),
            ("", styles['Normal']),
            ("EDUCACIÓN", styles['Heading2']),
            ("Grado en Ingeniería Informática", styles['Normal']),
            ("Universidad Politécnica de Madrid", styles['Normal']),
            ("2014 - 2018", styles['Normal']),
            ("", styles['Normal']),
            ("HABILIDADES TÉCNICAS", styles['Heading2']),
            ("• JavaScript, TypeScript, React, Angular", styles['Normal']),
            ("• Node.js, Express, MongoDB, PostgreSQL", styles['Normal']),
            ("• HTML5, CSS3, SASS, Bootstrap", styles['Normal']),
            ("• Git, Docker, AWS, Azure", styles['Normal']),
            ("", styles['Normal']),
            ("IDIOMAS", styles['Heading2']),
            ("• Español: Nativo", styles['Normal']),
            ("• Inglés: Avanzado (C1)", styles['Normal']),
            ("• Francés: Intermedio (B2)", styles['Normal']),
        ]
        
        # Agregar contenido al PDF
        for text, style in cv_content:
            if text == "":
                story.append(Spacer(1, 12))
            else:
                story.append(Paragraph(text, style))
        
        # Construir PDF
        doc.build(story)
        pdf_content = buffer.getvalue()
        buffer.close()
        
        return pdf_content
        
    except ImportError:
        print_error("ReportLab no disponible. Instala: pip install reportlab")
        return None
    except Exception as e:
        print_error(f"Error creando PDF de prueba: {str(e)}")
        return None

def test_document_intelligence_analysis(pdf_content):
    """Prueba el análisis con Document Intelligence"""
    try:
        print_info("Probando análisis con Document Intelligence...")
        
        from document_intelligence import analyze_cv_with_document_intelligence
        
        # Analizar CV
        result = analyze_cv_with_document_intelligence(pdf_content)
        
        if result.get("error"):
            print_error(f"Error en análisis: {result['error']}")
            return False
        
        if not result.get("document_intelligence_used"):
            print_info("Document Intelligence no disponible, usando método tradicional")
        
        # Mostrar resultados
        cv_info = result.get("cv_info", {})
        analysis = result.get("analysis", {})
        
        print_success("Análisis completado exitosamente")
        print("\n📊 RESULTADOS DEL ANÁLISIS:")
        print(f"• Habilidades técnicas: {len(cv_info.get('software', []))}")
        print(f"• Experiencias laborales: {len(cv_info.get('experiencia', []))}")
        print(f"• Formación académica: {len(cv_info.get('educacion', []))}")
        print(f"• Idiomas: {len(cv_info.get('idiomas', []))}")
        
        if analysis:
            print(f"• Puntuación de estructura: {analysis.get('structure_score', 0)}/100")
            print(f"• Puntuación de calidad: {analysis.get('quality_score', 0)}/100")
            
            if analysis.get("strengths"):
                print(f"• Fortalezas: {', '.join(analysis['strengths'])}")
            
            if analysis.get("weaknesses"):
                print(f"• Áreas de mejora: {', '.join(analysis['weaknesses'])}")
        
        return True
        
    except ImportError:
        print_error("Document Intelligence no disponible")
        return False
    except Exception as e:
        print_error(f"Error en análisis: {str(e)}")
        return False

def test_traditional_analysis(pdf_content):
    """Prueba el análisis tradicional para comparar"""
    try:
        print_info("Probando análisis tradicional para comparar...")
        
        from cv_analyzer import extract_pdf_info
        
        # Analizar CV
        result = extract_pdf_info(pdf_content)
        
        if result.get("error"):
            print_error(f"Error en análisis tradicional: {result['error']}")
            return False
        
        # Mostrar resultados
        cv_info = result.get("cv_info", {})
        
        print_success("Análisis tradicional completado")
        print(f"• Habilidades técnicas: {len(cv_info.get('software', []))}")
        print(f"• Experiencias laborales: {len(cv_info.get('experiencia', []))}")
        print(f"• Formación académica: {len(cv_info.get('educacion', []))}")
        
        return True
        
    except Exception as e:
        print_error(f"Error en análisis tradicional: {str(e)}")
        return False

def main():
    """Función principal"""
    print_header("PRUEBA DE AZURE AI DOCUMENT INTELLIGENCE")
    
    print_info("Este script prueba la funcionalidad de Document Intelligence")
    print_info("comparándola con el método tradicional de análisis de CVs.")
    
    # Verificar configuración
    endpoint = os.getenv('AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT')
    key = os.getenv('AZURE_DOCUMENT_INTELLIGENCE_KEY')
    
    if not endpoint or not key:
        print_error("Document Intelligence no configurado")
        print_info("Ejecuta: python setup_document_intelligence.py")
        return
    
    # Crear CV de prueba
    print_info("Creando CV de prueba...")
    pdf_content = create_test_cv_pdf()
    
    if not pdf_content:
        print_error("No se pudo crear el CV de prueba")
        return
    
    print_success(f"CV de prueba creado ({len(pdf_content)} bytes)")
    
    # Probar Document Intelligence
    doc_intelligence_ok = test_document_intelligence_analysis(pdf_content)
    
    # Probar método tradicional
    traditional_ok = test_traditional_analysis(pdf_content)
    
    # Resumen
    print_header("RESUMEN DE PRUEBAS")
    
    if doc_intelligence_ok:
        print_success("Document Intelligence: FUNCIONANDO")
    else:
        print_error("Document Intelligence: ERROR")
    
    if traditional_ok:
        print_success("Método tradicional: FUNCIONANDO")
    else:
        print_error("Método tradicional: ERROR")
    
    if doc_intelligence_ok and traditional_ok:
        print_info("Ambos métodos funcionan. Document Intelligence debería proporcionar")
        print_info("mejores resultados en la extracción de información estructurada.")

if __name__ == "__main__":
    main() 