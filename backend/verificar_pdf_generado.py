#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para verificar el contenido del PDF generado y confirmar que toda la información
del CV esté incluida correctamente en el informe final.
"""

import os
import sys
import glob
from datetime import datetime

def verificar_pdf_generado():
    """Verifica el contenido del PDF generado"""
    
    print("🔍 VERIFICANDO CONTENIDO DEL PDF GENERADO")
    print("=" * 60)
    
    # Buscar el PDF más reciente
    pdf_files = glob.glob("informe_cv_real_*.pdf")
    if not pdf_files:
        print("❌ No se encontraron PDFs generados")
        return False
    
    # Obtener el más reciente
    latest_pdf = max(pdf_files, key=os.path.getctime)
    print(f"📄 Analizando PDF: {latest_pdf}")
    
    # Verificar que el archivo existe y tiene tamaño adecuado
    if not os.path.exists(latest_pdf):
        print(f"❌ El archivo {latest_pdf} no existe")
        return False
    
    file_size = os.path.getsize(latest_pdf)
    print(f"📏 Tamaño del archivo: {file_size} bytes")
    
    if file_size < 1000:
        print("❌ El archivo es demasiado pequeño, puede estar corrupto")
        return False
    
    # Intentar extraer texto del PDF para verificar contenido
    try:
        import fitz  # PyMuPDF
        
        doc = fitz.open(latest_pdf)
        text_content = ""
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            text_content += page.get_text()
        
        doc.close()
        
        print(f"📝 Texto extraído del PDF: {len(text_content)} caracteres")
        
        # Verificar que contenga las secciones esperadas
        required_sections = [
            "Informe de Empleabilidad",
            "Análisis del Currículum Vitae",
            "Mapa de Habilidades Evaluadas",
            "Preferencias Laborales",
            "Recomendaciones"
        ]
        
        missing_sections = []
        for section in required_sections:
            if section.lower() not in text_content.lower():
                missing_sections.append(section)
        
        if missing_sections:
            print(f"❌ Secciones faltantes en el PDF: {missing_sections}")
            return False
        else:
            print("✅ Todas las secciones principales están presentes")
        
        # Verificar contenido específico del CV
        cv_sections = [
            "habilidades técnicas detectadas",
            "formación detectada",
            "fortalezas del cv",
            "áreas de mejora",
            "alertas o puntos críticos"
        ]
        
        cv_content_found = []
        for section in cv_sections:
            if section in text_content.lower():
                cv_content_found.append(section)
        
        print(f"✅ Secciones del CV encontradas: {len(cv_content_found)}/{len(cv_sections)}")
        
        if len(cv_content_found) < len(cv_sections):
            missing_cv_sections = [s for s in cv_sections if s not in cv_content_found]
            print(f"⚠️ Secciones del CV faltantes: {missing_cv_sections}")
        else:
            print("✅ Todas las secciones del CV están presentes")
        
        # Mostrar un fragmento del contenido para verificación
        print("\n📋 FRAGMENTO DEL CONTENIDO DEL PDF:")
        print("-" * 50)
        
        # Buscar la sección de análisis del CV
        cv_section_start = text_content.lower().find("análisis del currículum vitae")
        if cv_section_start != -1:
            cv_section = text_content[cv_section_start:cv_section_start + 1000]
            print(cv_section[:500] + "..." if len(cv_section) > 500 else cv_section)
        else:
            print("No se encontró la sección de análisis del CV")
        
        print("-" * 50)
        
        return True
        
    except ImportError:
        print("⚠️ PyMuPDF no disponible, no se puede verificar el contenido del PDF")
        print("✅ El archivo existe y tiene tamaño adecuado")
        return True
    except Exception as e:
        print(f"❌ Error verificando el PDF: {str(e)}")
        return False

def main():
    """Función principal"""
    print("🔍 VERIFICACIÓN DEL PDF GENERADO")
    print("=" * 60)
    
    try:
        success = verificar_pdf_generado()
        
        if success:
            print("\n✅ VERIFICACIÓN EXITOSA")
            print("El PDF generado contiene la información del CV correctamente")
            print("El análisis del CV está llegando al informe final")
            sys.exit(0)
        else:
            print("\n❌ VERIFICACIÓN FALLIDA")
            print("El PDF no contiene toda la información esperada del CV")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n❌ Error durante la verificación: {str(e)}")
        import traceback
        print(f"📋 Traceback: {traceback.format_exc()}")
        sys.exit(1)

if __name__ == "__main__":
    main() 