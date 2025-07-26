#!/usr/bin/env python3
"""
Script de prueba completa para EvaluaTE MVP
Prueba todo el flujo: datos personales → preferencias → minijuegos → análisis CV → informe final
"""

import requests
import json
import time
import os
from datetime import datetime

# Configuración
BACKEND_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:5173"

def print_step(step, description):
    """Imprime un paso del test con formato"""
    print(f"\n{'='*60}")
    print(f"🔍 PASO {step}: {description}")
    print(f"{'='*60}")

def print_success(message):
    """Imprime un mensaje de éxito"""
    print(f"✅ {message}")

def print_error(message):
    """Imprime un mensaje de error"""
    print(f"❌ {message}")

def print_info(message):
    """Imprime un mensaje informativo"""
    print(f"ℹ️ {message}")

def test_backend_health():
    """Test 1: Verificar que el backend está funcionando"""
    print_step(1, "VERIFICANDO SALUD DEL BACKEND")
    
    try:
        response = requests.get(f"{BACKEND_URL}/")
        if response.status_code == 200:
            data = response.json()
            print_success(f"Backend funcionando: {data['message']}")
            return True
        else:
            print_error(f"Backend no responde correctamente: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error conectando al backend: {str(e)}")
        return False

def test_log_scene():
    """Test 2: Simular logging de una escena de minijuego"""
    print_step(2, "SIMULANDO MINIJUEGO - TOMA DE DECISIONES")
    
    # Datos simulados de un minijuego de toma de decisiones
    scene_data = {
        "sceneId": 1,
        "decisions": [
            {
                "skill": "Toma de decisiones",
                "level": "Alto",
                "confidence": 0.85,
                "response": "Opción A - Enfrentar el problema directamente"
            },
            {
                "skill": "Resolución de problemas", 
                "level": "Medio",
                "confidence": 0.65,
                "response": "Analizar antes de actuar"
            }
        ],
        "totalSteps": 5,
        "totalTime": 180,  # 3 minutos
        "averageConfidence": 0.75,
        "emotionalTrend": ["positivo", "confiado"],
        "accessibilityUsed": False,
        "accessibilitySettings": {
            "easyReadingMode": False,
            "audioAssistiveMode": False,
            "showPictograms": False,
            "contrastLevel": "normal"
        }
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/api/logs/scene", json=scene_data)
        if response.status_code == 200:
            print_success("Escena de minijuego registrada correctamente")
            print_info(f"Respuesta: {response.json()}")
            return True
        else:
            print_error(f"Error registrando escena: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error en test de escena: {str(e)}")
        return False

def test_game_completion():
    """Test 3: Simular completado de un minijuego"""
    print_step(3, "SIMULANDO COMPLETADO DE MINIJUEGO")
    
    completion_data = {
        "sceneId": 1,
        "decisions": [
            {"skill": "Toma de decisiones", "level": "Alto", "confidence": 0.85},
            {"skill": "Resolución de problemas", "level": "Medio", "confidence": 0.65},
            {"skill": "Gestión emocional", "level": "Bajo", "confidence": 0.45}
        ],
        "completed": True,
        "timestamp": datetime.now().isoformat(),
        "finalScore": 75,
        "timeSpent": 300  # 5 minutos
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/api/logs/game-complete", json=completion_data)
        if response.status_code == 200:
            print_success("Minijuego marcado como completado")
            print_info(f"Respuesta: {response.json()}")
            return True
        else:
            print_error(f"Error completando juego: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error en test de completado: {str(e)}")
        return False

def test_cv_upload():
    """Test 4: Simular subida de CV"""
    print_step(4, "SIMULANDO SUBIDA DE CV")
    
    # Crear un archivo PDF simulado usando PyPDF2
    try:
        from pypdf import PdfWriter, PdfReader
        from io import BytesIO
        
        # Crear un PDF simple
        writer = PdfWriter()
        
        # Crear contenido de texto
        cv_content = """
        CURRICULUM VITAE
        
        DATOS PERSONALES
        Nombre: María García López
        Email: maria.garcia@email.com
        Teléfono: +34 612 345 678
        
        EXPERIENCIA LABORAL
        2020-2023: Desarrolladora Frontend en TechCorp
        - Desarrollo de aplicaciones web con React y TypeScript
        - Colaboración en equipo de 8 personas
        - Optimización de rendimiento web
        
        2018-2020: Técnica de Soporte en SoftServe
        - Atención al cliente técnico
        - Resolución de problemas de software
        - Documentación de procedimientos
        
        EDUCACIÓN
        2014-2018: Grado en Ingeniería Informática
        Universidad Politécnica de Madrid
        
        HABILIDADES TÉCNICAS
        - JavaScript, TypeScript, React
        - HTML, CSS, Bootstrap
        - Git, GitHub
        - Metodologías ágiles
        
        IDIOMAS
        - Español: Nativo
        - Inglés: B2
        - Francés: A2
        """
        
        # Crear un PDF simple (simulado)
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        from io import BytesIO
        
        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        p.drawString(100, 750, "CURRICULUM VITAE")
        p.drawString(100, 730, "María García López")
        p.drawString(100, 710, "maria.garcia@email.com")
        p.drawString(100, 690, "Desarrolladora Frontend")
        p.save()
        
        pdf_content = buffer.getvalue()
        buffer.close()
        
        # Guardar como archivo temporal
        with open("test_cv.pdf", "wb") as f:
            f.write(pdf_content)
        
        with open("test_cv.pdf", "rb") as f:
            files = {'file': ('test_cv.pdf', f, 'application/pdf')}
            response = requests.post(f"{BACKEND_URL}/api/upload-cv", files=files)
        
        if response.status_code == 200:
            data = response.json()
            print_success("CV subido correctamente")
            print_info(f"Archivo: {data['filename']}")
            print_info(f"Tamaño: {data['size']} bytes")
            print_info(f"Páginas: {data['pages']}")
            return True
        else:
            print_error(f"Error subiendo CV: {response.status_code}")
            print_error(f"Respuesta: {response.text}")
            return False
    except ImportError:
        print_error("reportlab no está instalado. Instalando...")
        import subprocess
        subprocess.run(["pip", "install", "reportlab"])
        return False
    except Exception as e:
        print_error(f"Error en test de subida: {str(e)}")
        return False
    finally:
        # Limpiar archivo temporal
        if os.path.exists("test_cv.pdf"):
            os.remove("test_cv.pdf")

def test_cv_analysis():
    """Test 5: Simular análisis de CV con IA"""
    print_step(5, "SIMULANDO ANÁLISIS DE CV CON IA")
    
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        from io import BytesIO
        
        # Crear un PDF simple para análisis
        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        p.drawString(100, 750, "CURRICULUM VITAE - DESARROLLADORA FRONTEND")
        p.drawString(100, 730, "María García López")
        p.drawString(100, 710, "maria.garcia@email.com")
        p.drawString(100, 690, "Desarrolladora Frontend Senior")
        p.drawString(100, 670, "Experiencia: React, TypeScript, JavaScript")
        p.drawString(100, 650, "Educación: Ingeniería Informática")
        p.save()
        
        pdf_content = buffer.getvalue()
        buffer.close()
        
        # Guardar como archivo temporal
        with open("test_cv_analysis.pdf", "wb") as f:
            f.write(pdf_content)
        
        # Datos simulados del usuario
        user_data = {
            'userId': 'test-user-001',
            'fullName': 'María García López',
            'softSkills': json.dumps([
                {"skill": "Toma de decisiones", "level": "Alto", "confidence": 0.85},
                {"skill": "Resolución de problemas", "level": "Medio", "confidence": 0.65},
                {"skill": "Gestión emocional", "level": "Bajo", "confidence": 0.45},
                {"skill": "Comunicación", "level": "Alto", "confidence": 0.80},
                {"skill": "Trabajo en equipo", "level": "Medio", "confidence": 0.70}
            ]),
            'jobPreferences': json.dumps({
                "areas": ["Desarrollo Frontend", "Desarrollo Web"],
                "needs": ["Horario flexible", "Trabajo remoto"],
                "workMode": "remoto",
                "availability": "completa",
                "willingToRelocate": False,
                "hasDisabilityCert": False
            }),
            'completedGames': json.dumps([1, 2, 3])
        }
        
        with open("test_cv_analysis.pdf", "rb") as f:
            files = {'file': ('test_cv_analysis.pdf', f, 'application/pdf')}
            response = requests.post(
                f"{BACKEND_URL}/api/pdf/analyze-cv", 
                files=files, 
                data=user_data
            )
        
        if response.status_code == 200:
            data = response.json()
            print_success("Análisis de CV completado con IA")
            print_info(f"Fortalezas detectadas: {len(data.get('strengths', []))}")
            print_info(f"Áreas de mejora: {len(data.get('weaknesses', []))}")
            print_info(f"Feedback: {data.get('feedback', 'N/A')[:100]}...")
            print_info(f"Habilidades técnicas: {data.get('skills', [])}")
            return True
        else:
            print_error(f"Error analizando CV: {response.status_code}")
            print_error(f"Respuesta: {response.text}")
            return False
    except Exception as e:
        print_error(f"Error en test de análisis: {str(e)}")
        return False
    finally:
        # Limpiar archivo temporal
        if os.path.exists("test_cv_analysis.pdf"):
            os.remove("test_cv_analysis.pdf")

def test_generate_report():
    """Test 6: Generar informe final completo"""
    print_step(6, "GENERANDO INFORME FINAL COMPLETO")
    
    # Datos completos para el informe (corregidos)
    report_data = {
        "userId": "test-user-001",
        "fullName": "María García López",
        "softSkills": [
            {"skill": "Toma de decisiones", "level": "Alto", "confidence": 0.85, "score": 85},
            {"skill": "Resolución de problemas", "level": "Medio", "confidence": 0.65, "score": 65},
            {"skill": "Gestión emocional", "level": "Bajo", "confidence": 0.45, "score": 45},
            {"skill": "Comunicación", "level": "Alto", "confidence": 0.80, "score": 80},
            {"skill": "Trabajo en equipo", "level": "Medio", "confidence": 0.70, "score": 70}
        ],
        "cvAnalysis": {
            "strengths": [
                "Experiencia sólida en desarrollo frontend",
                "Formación académica relevante",
                "Certificaciones técnicas actualizadas"
            ],
            "weaknesses": [
                "Falta experiencia en gestión de equipos grandes",
                "Necesita mejorar habilidades de presentación"
            ],
            "feedback": "CV bien estructurado con buena experiencia técnica. Áreas de mejora en liderazgo y comunicación pública.",
            "structure": "Clara y profesional",
            "coherence": "La experiencia es coherente con los objetivos profesionales",
            "experience": "5 años en desarrollo frontend con tecnologías modernas",
            "skills": ["React", "TypeScript", "JavaScript", "HTML5", "CSS3", "Git"],
            "education": ["Ingeniería Informática", "Certificaciones AWS y React"],
            "alerts": ["Considerar agregar más detalles sobre logros específicos"]
        },
        "jobPreferences": {
            "areas": ["Desarrollo Frontend", "Desarrollo Web"],
            "needs": ["Horario flexible", "Trabajo remoto"],
            "workMode": "remoto",
            "availability": "completa",
            "willingToRelocate": False,
            "hasDisabilityCert": False
        },
        "completedGames": [1, 2, 3],
        "logs": [
            {
                "sceneId": 1,
                "decisions": [
                    {"skill": "Toma de decisiones", "level": "Alto", "confidence": 0.85}
                ],
                "totalSteps": 5,
                "totalTime": 180,
                "averageConfidence": 0.75,
                "emotionalTrend": ["positivo", "confiado"],
                "accessibilityUsed": False
            }
        ]
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/api/logs/report", json=report_data)
        if response.status_code == 200:
            data = response.json()
            print_success("Informe final generado correctamente")
            print_info(f"Puntuación de empleabilidad: {data.get('employabilityScore', 'N/A')}")
            print_info(f"Nivel: {data.get('level', 'N/A')}")
            print_info(f"Resumen: {data.get('summary', 'N/A')}")
            
            # Mostrar recomendaciones
            recommendations = data.get('recommendations', {})
            if recommendations:
                print_info("Recomendaciones:")
                for category, items in recommendations.items():
                    if items:
                        print(f"  - {category}: {', '.join(items[:3])}")
            
            return True
        else:
            print_error(f"Error generando informe: {response.status_code}")
            print_error(f"Respuesta: {response.text}")
            return False
    except Exception as e:
        print_error(f"Error en test de informe: {str(e)}")
        return False

def test_frontend_access():
    """Test 7: Verificar acceso al frontend"""
    print_step(7, "VERIFICANDO ACCESO AL FRONTEND")
    
    try:
        response = requests.get(f"{FRONTEND_URL}", timeout=5)
        if response.status_code == 200:
            print_success("Frontend accesible correctamente")
            return True
        else:
            print_error(f"Frontend no responde correctamente: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print_error("Frontend no está ejecutándose en el puerto 5173")
        print_info("Ejecuta: cd nuevo-frontend && npm run dev")
        return False
    except Exception as e:
        print_error(f"Error verificando frontend: {str(e)}")
        return False

def main():
    """Función principal que ejecuta todos los tests"""
    print("🚀 INICIANDO PRUEBA COMPLETA DE EVALUATE MVP")
    print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    tests = [
        ("Salud del Backend", test_backend_health),
        ("Logging de Escena", test_log_scene),
        ("Completado de Juego", test_game_completion),
        ("Subida de CV", test_cv_upload),
        ("Análisis de CV", test_cv_analysis),
        ("Generación de Informe", test_generate_report),
        ("Acceso al Frontend", test_frontend_access)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print_error(f"Error inesperado en {test_name}: {str(e)}")
            results.append((test_name, False))
    
    # Resumen final
    print(f"\n{'='*60}")
    print("📊 RESUMEN DE PRUEBAS")
    print(f"{'='*60}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASÓ" if result else "❌ FALLÓ"
        print(f"{status} - {test_name}")
    
    print(f"\n🎯 RESULTADO FINAL: {passed}/{total} pruebas exitosas")
    
    if passed == total:
        print("🎉 ¡TODAS LAS PRUEBAS PASARON! La aplicación está funcionando correctamente.")
    elif passed >= total * 0.8:
        print("⚠️ La mayoría de las pruebas pasaron. Revisa los errores antes de producción.")
    else:
        print("❌ Muchas pruebas fallaron. Revisa la configuración y logs.")
    
    print(f"\n🔗 URLs de la aplicación:")
    print(f"   Backend: {BACKEND_URL}")
    print(f"   Frontend: {FRONTEND_URL}")
    print(f"   API Docs: {BACKEND_URL}/docs")

if __name__ == "__main__":
    main() 