#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de prueba para verificar el funcionamiento del OCR en CVs
"""

import sys
import os
from cv_analyzer import extract_pdf_info

def test_cv_analysis(pdf_path: str):
    """
    Prueba el análisis de un CV específico
    """
    try:
        print(f"Probando análisis de: {pdf_path}")
        
        if not os.path.exists(pdf_path):
            print(f"Error: El archivo {pdf_path} no existe")
            return
        
        with open(pdf_path, 'rb') as f:
            pdf_buffer = f.read()
        
        print(f"Archivo leído: {len(pdf_buffer)} bytes")
        
        # Analizar el CV
        result = extract_pdf_info(pdf_buffer)
        
        if "error" in result:
            print(f"Error en análisis: {result['error']}")
            return
        
        # Mostrar resultados
        analysis = result.get("analysis", {})
        cv_info = result.get("cv_info", {})
        
        print("\n=== RESULTADOS DEL ANÁLISIS ===")
        print(f"Estructura: {analysis.get('structure', 'N/A')}")
        print(f"Coherencia: {analysis.get('coherence', 'N/A')}")
        print(f"Experiencia: {analysis.get('experience', 'N/A')}")
        print(f"Habilidades encontradas: {len(analysis.get('skills', []))}")
        print(f"Soft Skills encontradas: {len(analysis.get('softSkills', []))}")
        print(f"Idiomas encontrados: {len(analysis.get('languages', []))}")
        print(f"Experiencias encontradas: {len(cv_info.get('experiencia', []))}")
        print(f"Educación encontrada: {len(cv_info.get('educacion', []))}")
        
        if analysis.get('skills'):
            print(f"Habilidades técnicas: {', '.join(analysis['skills'])}")
        
        if analysis.get('softSkills'):
            print(f"Soft Skills: {', '.join(analysis['softSkills'])}")
        
        if analysis.get('languages'):
            idiomas_str = []
            for lang in analysis['languages']:
                idioma = lang.get('idioma', '')
                nivel = lang.get('nivel', '')
                idiomas_str.append(f"{idioma} ({nivel})")
            print(f"Idiomas: {', '.join(idiomas_str)}")
        
        if analysis.get('strengths'):
            print(f"Fortalezas: {', '.join(analysis['strengths'])}")
        
        if analysis.get('weaknesses'):
            print(f"Debilidades: {', '.join(analysis['weaknesses'])}")
        
        if analysis.get('feedback'):
            print(f"Feedback: {analysis['feedback']}")
        
        if analysis.get('alerts'):
            print(f"Alertas: {', '.join(analysis['alerts'])}")
        
        print(f"\nTexto extraído (primeros 500 caracteres):")
        print(result.get('raw_text', '')[:500])
        
    except Exception as e:
        print(f"Error en prueba: {e}")

def main():
    if len(sys.argv) < 2:
        print("Uso: python test_ocr.py <ruta_al_pdf>")
        print("Ejemplo: python test_ocr.py cv_prueba.pdf")
        return
    
    pdf_path = sys.argv[1]
    test_cv_analysis(pdf_path)

if __name__ == "__main__":
    main() 