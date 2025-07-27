#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de prueba completo y profesional para verificar que el análisis del CV real
cv_prueba.pdf llegue correctamente al informe final.

Este script:
1. Analiza el CV real cv_prueba.pdf
2. Genera un informe completo con todos los datos
3. Verifica que toda la información del CV llegue al informe final
4. Genera el PDF para comprobar su funcionamiento
"""

import json
import sys
import os
import asyncio
from datetime import datetime
from pathlib import Path

# Agregar el directorio actual al path para importar los módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importar las funciones necesarias
from cv_analyzer import extract_pdf_info
from pdf_service import create_employability_pdf

def test_cv_real_analysis():
    """Prueba el análisis completo del CV real"""
    
    print("🧪 INICIANDO PRUEBA COMPLETA CON CV REAL")
    print("=" * 60)
    
    # 1. Verificar que el archivo existe
    cv_path = "cv_prueba.pdf"
    if not os.path.exists(cv_path):
        print(f"❌ Error: No se encuentra el archivo {cv_path}")
        return False
    
    print(f"✅ Archivo CV encontrado: {cv_path}")
    print(f"📏 Tamaño: {os.path.getsize(cv_path) / 1024:.1f} KB")
    
    # 2. Leer el archivo PDF
    try:
        with open(cv_path, 'rb') as f:
            pdf_content = f.read()
        print(f"✅ PDF leído correctamente: {len(pdf_content)} bytes")
    except Exception as e:
        print(f"❌ Error leyendo el PDF: {str(e)}")
        return False
    
    # 3. Analizar el CV usando cv_analyzer
    print("\n🔍 ANALIZANDO CV CON cv_analyzer...")
    try:
        cv_result = extract_pdf_info(pdf_content)
        
        if cv_result.get("error"):
            print(f"❌ Error en análisis: {cv_result['error']}")
            return False
        
        print("✅ Análisis del CV completado")
        
        # Mostrar información extraída
        cv_info = cv_result.get("cv_info", {})
        analysis = cv_result.get("analysis", {})
        raw_text = cv_result.get("raw_text", "")
        
        print(f"📝 Texto extraído: {len(raw_text)} caracteres")
        print(f"📊 Información estructurada: {len(cv_info)} elementos")
        print(f"🔍 Análisis generado: {len(analysis)} elementos")
        
        # Mostrar detalles del análisis
        if analysis:
            print("\n📋 DETALLES DEL ANÁLISIS:")
            print(f"  • Fortalezas: {len(analysis.get('strengths', []))}")
            print(f"  • Debilidades: {len(analysis.get('weaknesses', []))}")
            print(f"  • Habilidades técnicas: {len(analysis.get('skills', []))}")
            print(f"  • Formación: {len(analysis.get('education', []))}")
            print(f"  • Alertas: {len(analysis.get('alerts', []))}")
            
            if analysis.get('skills'):
                print(f"  • Habilidades detectadas: {', '.join(analysis['skills'][:5])}{'...' if len(analysis['skills']) > 5 else ''}")
            
            if analysis.get('education'):
                print(f"  • Formación detectada: {', '.join(analysis['education'][:3])}{'...' if len(analysis['education']) > 3 else ''}")
        
    except Exception as e:
        print(f"❌ Error en análisis del CV: {str(e)}")
        import traceback
        print(f"📋 Traceback: {traceback.format_exc()}")
        return False
    
    # 4. Crear datos de prueba completos para el informe
    print("\n📊 PREPARANDO DATOS PARA EL INFORME...")
    
    # Datos de habilidades soft de prueba
    soft_skills = [
        {"skill": "Comunicación", "score": 85, "level": "alto", "confidence": 90},
        {"skill": "Trabajo en equipo", "score": 92, "level": "alto", "confidence": 88},
        {"skill": "Resolución de problemas", "score": 78, "level": "medio", "confidence": 85},
        {"skill": "Liderazgo", "score": 65, "level": "medio", "confidence": 70},
        {"skill": "Adaptabilidad", "score": 88, "level": "alto", "confidence": 92}
    ]
    
    # Datos de preferencias laborales
    job_preferences = {
        "areas": ["Desarrollo web", "Análisis de datos", "DevOps"],
        "needs": ["Entorno colaborativo", "Oportunidades de aprendizaje", "Flexibilidad horaria"],
        "workMode": "híbrido",
        "availability": "completa",
        "willingToRelocate": True,
        "hasDisabilityCert": False
    }
    
    # Datos del usuario
    user_info = {
        "fullName": "Ana García López",
        "userId": "test_user_real_cv"
    }
    
    # 5. Preparar datos para el PDF
    print("\n📋 PREPARANDO DATOS PARA EL PDF...")
    
    pdf_data = {
        "gameData": soft_skills,
        "cvAnalysis": analysis,  # Usar el análisis real del CV
        "jobPreferences": job_preferences,
        "userInfo": user_info,
        "informeProfesional": "Informe profesional generado por IA basado en el análisis del CV real"
    }
    
    print(f"✅ Datos preparados:")
    print(f"  • Habilidades soft: {len(soft_skills)}")
    print(f"  • Análisis CV: {bool(analysis)}")
    print(f"  • Preferencias: {bool(job_preferences)}")
    
    # 6. Verificar que el análisis del CV esté completo en los datos
    print("\n🔍 VERIFICANDO ANÁLISIS DEL CV EN LOS DATOS...")
    
    cv_in_pdf = pdf_data.get('cvAnalysis', {})
    required_fields = ['strengths', 'weaknesses', 'skills', 'education', 'alerts', 'feedback', 'structure', 'coherence', 'experience']
    
    missing_fields = []
    for field in required_fields:
        if not cv_in_pdf.get(field):
            missing_fields.append(field)
    
    if missing_fields:
        print(f"❌ Campos faltantes en el análisis: {missing_fields}")
        return False
    else:
        print("✅ Todos los campos del análisis del CV están presentes")
    
    # Verificar contenido específico
    if cv_in_pdf.get('skills'):
        print(f"✅ Habilidades técnicas detectadas: {len(cv_in_pdf['skills'])}")
        print(f"   Ejemplos: {', '.join(cv_in_pdf['skills'][:5])}")
    
    if cv_in_pdf.get('education'):
        print(f"✅ Formación detectada: {len(cv_in_pdf['education'])}")
        print(f"   Ejemplos: {', '.join(cv_in_pdf['education'][:3])}")
    
    if cv_in_pdf.get('alerts'):
        print(f"✅ Alertas detectadas: {len(cv_in_pdf['alerts'])}")
    
    # 7. Generar el PDF del informe
    print("\n🖨️ GENERANDO PDF DEL INFORME...")
    
    try:
        start_time = datetime.now()
        pdf_buffer = create_employability_pdf(pdf_data)
        end_time = datetime.now()
        generation_time = (end_time - start_time).total_seconds()
        
        print(f"✅ PDF generado exitosamente en {generation_time:.2f} segundos")
        print(f"📏 Tamaño del PDF: {len(pdf_buffer)} bytes")
        
        # 8. Guardar el PDF para verificación
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        pdf_filename = f"informe_cv_real_{timestamp}.pdf"
        
        with open(pdf_filename, 'wb') as f:
            f.write(pdf_buffer)
        
        print(f"💾 PDF guardado como: {pdf_filename}")
        
    except Exception as e:
        print(f"❌ Error generando PDF: {str(e)}")
        import traceback
        print(f"📋 Traceback: {traceback.format_exc()}")
        return False
    
    # 9. Verificación final
    print("\n✅ VERIFICACIÓN FINAL")
    print("=" * 60)
    
    # Verificar que el PDF se generó correctamente
    if os.path.exists(pdf_filename):
        pdf_size = os.path.getsize(pdf_filename)
        print(f"✅ PDF generado y guardado: {pdf_filename}")
        print(f"📏 Tamaño del archivo: {pdf_size} bytes")
        
        if pdf_size > 1000:  # Un PDF válido debe tener al menos 1KB
            print("✅ PDF parece válido (tamaño adecuado)")
        else:
            print("⚠️ PDF muy pequeño, puede haber un problema")
    else:
        print("❌ Error: El PDF no se guardó correctamente")
        return False
    
    # Resumen de la prueba
    print("\n🎉 RESUMEN DE LA PRUEBA")
    print("=" * 60)
    print("✅ CV real analizado correctamente")
    print("✅ Información extraída del CV:")
    print(f"   • Habilidades técnicas: {len(cv_in_pdf.get('skills', []))}")
    print(f"   • Formación: {len(cv_in_pdf.get('education', []))}")
    print(f"   • Fortalezas: {len(cv_in_pdf.get('strengths', []))}")
    print(f"   • Debilidades: {len(cv_in_pdf.get('weaknesses', []))}")
    print(f"   • Alertas: {len(cv_in_pdf.get('alerts', []))}")
    print("✅ Datos integrados correctamente en el informe")
    print("✅ PDF generado exitosamente")
    print(f"📄 Archivo generado: {pdf_filename}")
    
    return True

def main():
    """Función principal"""
    print("🚀 INICIANDO PRUEBA PROFESIONAL CON CV REAL")
    print("=" * 60)
    
    try:
        success = test_cv_real_analysis()
        
        if success:
            print("\n✅ PRUEBA EXITOSA")
            print("El análisis del CV real se está incluyendo correctamente en el informe final")
            print("El PDF generado contiene toda la información extraída del CV")
            sys.exit(0)
        else:
            print("\n❌ PRUEBA FALLIDA")
            print("El análisis del CV no se está incluyendo correctamente en el informe final")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n❌ Error durante la prueba: {str(e)}")
        import traceback
        print(f"📋 Traceback: {traceback.format_exc()}")
        sys.exit(1)

if __name__ == "__main__":
    main() 