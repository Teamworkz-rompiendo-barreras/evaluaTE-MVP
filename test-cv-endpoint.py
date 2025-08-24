#!/usr/bin/env python3
"""
Script de prueba para diagnosticar el endpoint de análisis de CV
"""

import requests
import json
import os

def test_cv_endpoint():
    """Prueba el endpoint de análisis de CV"""
    
    print("🔍 DIAGNÓSTICO DEL ENDPOINT DE ANÁLISIS DE CV")
    print("=" * 50)
    
    # URL del endpoint
    url = "http://localhost:8080/api/pdf/analyze-cv"
    
    # 1. Verificar que el backend esté funcionando
    print("\n1️⃣ Verificando estado del backend...")
    try:
        health_response = requests.get("http://localhost:8080/health")
        if health_response.status_code == 200:
            print("✅ Backend funcionando correctamente")
            print(f"📊 Respuesta: {health_response.json()}")
        else:
            print(f"❌ Backend no responde correctamente: {health_response.status_code}")
            return
    except Exception as e:
        print(f"❌ Error conectando al backend: {e}")
        return
    
    # 2. Crear un archivo PDF de prueba simple
    print("\n2️⃣ Creando archivo PDF de prueba...")
    test_pdf_path = "test-cv.pdf"
    
    # Crear un PDF simple usando reportlab si está disponible
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        
        c = canvas.Canvas(test_pdf_path, pagesize=letter)
        c.drawString(100, 750, "CV DE PRUEBA")
        c.drawString(100, 700, "Nombre: Ester Pérez Ribada")
        c.drawString(100, 650, "Experiencia: Desarrolladora Frontend")
        c.drawString(100, 600, "Habilidades: React, TypeScript, CSS")
        c.save()
        print(f"✅ PDF de prueba creado: {test_pdf_path}")
        
    except ImportError:
        print("⚠️ ReportLab no disponible, creando archivo de texto...")
        with open(test_pdf_path, "w") as f:
            f.write("CV DE PRUEBA\n")
            f.write("Nombre: Ester Pérez Ribada\n")
            f.write("Experiencia: Desarrolladora Frontend\n")
            f.write("Habilidades: React, TypeScript, CSS\n")
        print(f"✅ Archivo de texto creado: {test_pdf_path}")
    
    # 3. Preparar datos de prueba
    print("\n3️⃣ Preparando datos de prueba...")
    
    test_data = {
        "softSkillsJson": json.dumps([
            {"skill": "Toma de decisiones", "score": 85, "level": "Alto"},
            {"skill": "Pensamiento Analítico", "score": 78, "level": "Medio-Alto"}
        ]),
        "jobPreferencesJson": json.dumps({
            "areas": ["Desarrollo Frontend", "UI/UX"],
            "workMode": "Remoto",
            "availability": "Inmediata"
        }),
        "completedGamesJson": json.dumps(["decision-making", "analytical-thinking"]),
        "logsJson": json.dumps(["Juego completado: Toma de decisiones", "Juego completado: Pensamiento Analítico"])
    }
    
    print("✅ Datos de prueba preparados")
    
    # 4. Probar el endpoint
    print("\n4️⃣ Probando endpoint de análisis de CV...")
    
    try:
        with open(test_pdf_path, "rb") as f:
            files = {"file": (test_pdf_path, f, "application/pdf")}
            
            print(f"📤 Enviando archivo: {test_pdf_path}")
            print(f"📊 Tamaño del archivo: {os.path.getsize(test_pdf_path)} bytes")
            
            response = requests.post(
                url,
                files=files,
                data=test_data,
                timeout=30
            )
            
            print(f"📥 Respuesta recibida: {response.status_code}")
            print(f"📋 Headers de respuesta: {dict(response.headers)}")
            
            if response.status_code == 200:
                print("✅ Endpoint funcionando correctamente!")
                result = response.json()
                print(f"📊 Resultado: {json.dumps(result, indent=2, ensure_ascii=False)}")
                
            elif response.status_code == 500:
                print("❌ Error 500 del servidor")
                try:
                    error_detail = response.json()
                    print(f"🔍 Detalle del error: {json.dumps(error_detail, indent=2, ensure_ascii=False)}")
                except:
                    print(f"🔍 Texto del error: {response.text}")
                    
            else:
                print(f"⚠️ Respuesta inesperada: {response.status_code}")
                print(f"🔍 Contenido: {response.text}")
                
    except Exception as e:
        print(f"❌ Error durante la prueba: {e}")
        print(f"🔍 Tipo de error: {type(e).__name__}")
        
    finally:
        # Limpiar archivo de prueba
        if os.path.exists(test_pdf_path):
            os.remove(test_pdf_path)
            print(f"🧹 Archivo de prueba eliminado: {test_pdf_path}")
    
    # 5. Verificar logs del backend
    print("\n5️⃣ Verificando posibles problemas...")
    
    # Verificar si hay variables de entorno necesarias
    env_vars = [
        "AZURE_DI_MODEL_ID",
        "AZURE_DI_ENDPOINT", 
        "AZURE_DI_KEY"
    ]
    
    print("🔧 Variables de entorno:")
    for var in env_vars:
        value = os.getenv(var)
        if value:
            print(f"   ✅ {var}: {value[:20]}..." if len(value) > 20 else f"   ✅ {var}: {value}")
        else:
            print(f"   ❌ {var}: No configurada")
    
    print("\n🎯 DIAGNÓSTICO COMPLETADO")
    print("=" * 50)

if __name__ == "__main__":
    test_cv_endpoint()
