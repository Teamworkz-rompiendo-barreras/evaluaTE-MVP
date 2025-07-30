#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de prueba para verificar el funcionamiento del endpoint de análisis de CV
"""

import requests
import json
import os
from pathlib import Path

def test_cv_analysis_endpoint():
    """Prueba el endpoint de análisis de CV"""
    
    # URL del endpoint
    url = "http://localhost:8000/api/pdf/analyze-cv"
    
    # Crear un PDF de prueba simple
    test_pdf_path = "test_cv.pdf"
    
    # Crear un PDF de prueba básico
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        
        c = canvas.Canvas(test_pdf_path, pagesize=letter)
        c.drawString(100, 750, "CURRICULUM VITAE")
        c.drawString(100, 720, "Nombre: Juan Pérez")
        c.drawString(100, 700, "Email: juan.perez@email.com")
        c.drawString(100, 680, "Teléfono: +34 123 456 789")
        c.drawString(100, 640, "EXPERIENCIA LABORAL")
        c.drawString(100, 620, "Desarrollador Full Stack - Empresa ABC (2020-2023)")
        c.drawString(100, 600, "- Desarrollo de aplicaciones web con React y Node.js")
        c.drawString(100, 580, "- Gestión de bases de datos SQL y NoSQL")
        c.drawString(100, 540, "EDUCACIÓN")
        c.drawString(100, 520, "Ingeniería Informática - Universidad XYZ (2016-2020)")
        c.drawString(100, 480, "HABILIDADES TÉCNICAS")
        c.drawString(100, 460, "- JavaScript, Python, Java")
        c.drawString(100, 440, "- React, Node.js, Django")
        c.drawString(100, 420, "- SQL, MongoDB, Redis")
        c.drawString(100, 400, "- Git, Docker, AWS")
        c.save()
        
        print("✅ PDF de prueba creado exitosamente")
        
    except ImportError:
        print("⚠️ reportlab no disponible, creando archivo de texto simple")
        # Crear un archivo de texto simple como fallback
        with open(test_pdf_path, 'w') as f:
            f.write("CURRICULUM VITAE\n")
            f.write("Nombre: Juan Pérez\n")
            f.write("Email: juan.perez@email.com\n")
            f.write("Teléfono: +34 123 456 789\n")
            f.write("EXPERIENCIA LABORAL\n")
            f.write("Desarrollador Full Stack - Empresa ABC (2020-2023)\n")
            f.write("- Desarrollo de aplicaciones web con React y Node.js\n")
            f.write("- Gestión de bases de datos SQL y NoSQL\n")
            f.write("EDUCACIÓN\n")
            f.write("Ingeniería Informática - Universidad XYZ (2016-2020)\n")
            f.write("HABILIDADES TÉCNICAS\n")
            f.write("- JavaScript, Python, Java\n")
            f.write("- React, Node.js, Django\n")
            f.write("- SQL, MongoDB, Redis\n")
            f.write("- Git, Docker, AWS\n")
    
    # Preparar los datos para la petición
    data = {
        'userId': 'test-user-123',
        'fullName': 'Juan Pérez',
        'softSkills': json.dumps([]),
        'jobPreferences': json.dumps({}),
        'completedGames': json.dumps([])
    }
    
    # Preparar el archivo
    files = {
        'file': ('test_cv.pdf', open(test_pdf_path, 'rb'), 'application/pdf')
    }
    
    try:
        print("🚀 Enviando petición al endpoint...")
        print(f"URL: {url}")
        print(f"Datos: {data}")
        
        # Realizar la petición
        response = requests.post(url, data=data, files=files, timeout=60)
        
        print(f"📥 Respuesta recibida:")
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Análisis exitoso!")
            print(f"Resultado: {json.dumps(result, indent=2, ensure_ascii=False)}")
            
            # Verificar estructura del resultado
            expected_fields = ['strengths', 'weaknesses', 'feedback', 'skills', 'education']
            missing_fields = [field for field in expected_fields if field not in result]
            
            if missing_fields:
                print(f"⚠️ Campos faltantes en la respuesta: {missing_fields}")
            else:
                print("✅ Todos los campos esperados están presentes")
                
        else:
            print(f"❌ Error en la respuesta:")
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión: {e}")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
    finally:
        # Limpiar archivo de prueba
        if os.path.exists(test_pdf_path):
            os.remove(test_pdf_path)
            print("🧹 Archivo de prueba eliminado")

def test_document_intelligence_direct():
    """Prueba directa del módulo de Document Intelligence"""
    
    print("\n🔍 Probando Document Intelligence directamente...")
    
    try:
        from document_intelligence import analyze_cv_with_document_intelligence
        
        # Crear un PDF de prueba
        test_pdf_path = "test_di.pdf"
        try:
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import letter
            c = canvas.Canvas(test_pdf_path, pagesize=letter)
            c.drawString(100, 750, "CURRICULUM VITAE")
            c.drawString(100, 720, "Nombre: María García")
            c.drawString(100, 700, "Email: maria.garcia@email.com")
            c.drawString(100, 680, "Teléfono: +34 987 654 321")
            c.drawString(100, 640, "EXPERIENCIA LABORAL")
            c.drawString(100, 620, "Desarrolladora Frontend - Empresa DEF (2021-2024)")
            c.drawString(100, 600, "- Desarrollo de interfaces con React y TypeScript")
            c.drawString(100, 580, "- Optimización de rendimiento web")
            c.drawString(100, 540, "EDUCACIÓN")
            c.drawString(100, 520, "Grado en Ingeniería Informática - Universidad ABC (2017-2021)")
            c.drawString(100, 480, "HABILIDADES TÉCNICAS")
            c.drawString(100, 460, "- TypeScript, JavaScript, HTML, CSS")
            c.drawString(100, 440, "- React, Vue.js, Angular")
            c.drawString(100, 420, "- Node.js, Express")
            c.drawString(100, 400, "- Git, Webpack, Jest")
            c.save()
        except ImportError:
            with open(test_pdf_path, 'w') as f:
                f.write("CURRICULUM VITAE\n")
                f.write("Nombre: María García\n")
                f.write("Email: maria.garcia@email.com\n")
                f.write("Teléfono: +34 987 654 321\n")
                f.write("EXPERIENCIA LABORAL\n")
                f.write("Desarrolladora Frontend - Empresa DEF (2021-2024)\n")
                f.write("- Desarrollo de interfaces con React y TypeScript\n")
                f.write("- Optimización de rendimiento web\n")
                f.write("EDUCACIÓN\n")
                f.write("Grado en Ingeniería Informática - Universidad ABC (2017-2021)\n")
                f.write("HABILIDADES TÉCNICAS\n")
                f.write("- TypeScript, JavaScript, HTML, CSS\n")
                f.write("- React, Vue.js, Angular\n")
                f.write("- Node.js, Express\n")
                f.write("- Git, Webpack, Jest\n")
        
        # Leer el archivo
        with open(test_pdf_path, 'rb') as f:
            pdf_content = f.read()
        
        # Analizar con Document Intelligence
        result = analyze_cv_with_document_intelligence(pdf_content)
        
        print("✅ Análisis con Document Intelligence completado!")
        print(f"Resultado: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
        # Limpiar
        os.remove(test_pdf_path)
        
    except Exception as e:
        print(f"❌ Error en Document Intelligence: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    print("🧪 Iniciando pruebas de análisis de CV...")
    
    # Probar el endpoint
    test_cv_analysis_endpoint()
    
    # Probar Document Intelligence directamente
    test_document_intelligence_direct()
    
    print("\n✅ Pruebas completadas") 