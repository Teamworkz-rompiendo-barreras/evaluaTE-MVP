#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de prueba para el nuevo sistema de análisis de CV
"""

import os
import sys
import json
from pathlib import Path

# Agregar el directorio actual al path para importar cv_analyzer
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from cv_analyzer import extract_pdf_info, extract_text_with_advanced_ocr

def test_cv_analysis():
    """
    Prueba el sistema de análisis de CV
    """
    print("🧪 Iniciando pruebas del sistema de análisis de CV...")
    
    # Buscar archivos PDF en el directorio
    pdf_files = list(Path('.').glob('*.pdf'))
    
    if not pdf_files:
        print("❌ No se encontraron archivos PDF para probar")
        print("   Coloca un archivo PDF en el directorio backend/ para realizar las pruebas")
        return
    
    print(f"📄 Archivos PDF encontrados: {len(pdf_files)}")
    
    for pdf_file in pdf_files:
        print(f"\n🔍 Probando archivo: {pdf_file.name}")
        
        try:
            # Leer el archivo PDF
            with open(pdf_file, 'rb') as f:
                pdf_buffer = f.read()
            
            print(f"   📊 Tamaño del archivo: {len(pdf_buffer)} bytes")
            
            # Probar extracción de texto
            print("   📝 Extrayendo texto...")
            text = extract_text_with_advanced_ocr(pdf_buffer)
            print(f"   ✅ Texto extraído: {len(text)} caracteres")
            
            if len(text.strip()) < 50:
                print("   ⚠️  Poco texto extraído, puede ser un PDF escaneado")
            
            # Probar análisis completo
            print("   🤖 Analizando CV con IA...")
            result = extract_pdf_info(pdf_buffer)
            
            if result.get("error"):
                print(f"   ❌ Error en análisis: {result['error']}")
                continue
            
            # Mostrar resultados
            analysis = result.get("analysis", {})
            cv_info = result.get("cv_info", {})
            full_data = result.get("full_cv_data", {})
            
            print("   📊 Resultados del análisis:")
            print(f"      • Estructura: {analysis.get('structure', 'N/A')}")
            print(f"      • Coherencia: {analysis.get('coherence', 'N/A')}")
            print(f"      • Experiencia: {analysis.get('experience', 'N/A')}")
            print(f"      • Años de experiencia: {analysis.get('total_years_experience', 0)}")
            
            # Información de contacto
            contact = full_data.get("contacto", {})
            if contact:
                print("   📞 Información de contacto:")
                if contact.get("nombre"):
                    print(f"      • Nombre: {contact['nombre']}")
                if contact.get("email"):
                    print(f"      • Email: {contact['email']}")
                if contact.get("telefono"):
                    print(f"      • Teléfono: {contact['telefono']}")
            
            # Experiencia laboral
            experience = full_data.get("experiencia_laboral", [])
            if experience:
                print(f"   💼 Experiencia laboral: {len(experience)} puestos")
                for i, exp in enumerate(experience[:3], 1):  # Mostrar solo los primeros 3
                    print(f"      {i}. {exp.get('cargo', 'N/A')} en {exp.get('empresa', 'N/A')}")
                    print(f"         {exp.get('fecha_inicio', 'N/A')} - {exp.get('fecha_fin', 'N/A')}")
            
            # Formación académica
            education = full_data.get("formacion_academica", [])
            if education:
                print(f"   🎓 Formación académica: {len(education)} elementos")
                for i, edu in enumerate(education[:3], 1):  # Mostrar solo los primeros 3
                    print(f"      {i}. {edu.get('titulo', 'N/A')}")
                    print(f"         {edu.get('institucion', 'N/A')}")
            
            # Habilidades técnicas
            skills = full_data.get("habilidades_tecnicas", [])
            if skills:
                print(f"   🔧 Habilidades técnicas: {len(skills)} detectadas")
                print(f"      • {', '.join(skills[:10])}")  # Mostrar solo las primeras 10
            
            # Idiomas
            languages = full_data.get("idiomas", [])
            if languages:
                print(f"   🌍 Idiomas: {len(languages)} detectados")
                for lang in languages:
                    print(f"      • {lang.get('idioma', 'N/A')} ({lang.get('nivel', 'N/A')})")
            
            # Proyectos
            projects = full_data.get("proyectos", [])
            if projects:
                print(f"   🚀 Proyectos: {len(projects)} detectados")
            
            # Fortalezas y debilidades
            strengths = analysis.get("strengths", [])
            weaknesses = analysis.get("weaknesses", [])
            
            if strengths:
                print(f"   ✅ Fortalezas: {len(strengths)} detectadas")
                for strength in strengths[:3]:  # Mostrar solo las primeras 3
                    print(f"      • {strength}")
            
            if weaknesses:
                print(f"   ⚠️  Áreas de mejora: {len(weaknesses)} detectadas")
                for weakness in weaknesses[:3]:  # Mostrar solo las primeras 3
                    print(f"      • {weakness}")
            
            print("   ✅ Análisis completado exitosamente")
            
        except Exception as e:
            print(f"   ❌ Error procesando {pdf_file.name}: {str(e)}")
    
    print("\n🎉 Pruebas completadas")

def test_ocr_only():
    """
    Prueba solo la extracción de texto con OCR
    """
    print("🧪 Probando solo extracción de texto con OCR...")
    
    pdf_files = list(Path('.').glob('*.pdf'))
    
    if not pdf_files:
        print("❌ No se encontraron archivos PDF")
        return
    
    for pdf_file in pdf_files[:1]:  # Probar solo el primer archivo
        print(f"📄 Probando OCR en: {pdf_file.name}")
        
        try:
            with open(pdf_file, 'rb') as f:
                pdf_buffer = f.read()
            
            text = extract_text_with_advanced_ocr(pdf_buffer)
            
            print(f"✅ Texto extraído: {len(text)} caracteres")
            print("📝 Primeras 500 caracteres:")
            print("-" * 50)
            print(text[:500])
            print("-" * 50)
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "ocr":
        test_ocr_only()
    else:
        test_cv_analysis()