#!/usr/bin/env python3
"""
Test Final Simplificado - EvaluaTE MVP
Verifica las funcionalidades críticas del backend
"""

import requests
import json
from datetime import datetime

BACKEND_URL = "http://localhost:8000"

def test_critical_functionality():
    """Test de funcionalidades críticas"""
    print("🚀 TEST FINAL - EVALUATE MVP")
    print("=" * 50)
    
    # Test 1: Backend Health
    print("1. ✅ Verificando backend...")
    try:
        response = requests.get(f"{BACKEND_URL}/")
        if response.status_code == 200:
            print("   Backend funcionando correctamente")
        else:
            print(f"   ❌ Error: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Error conectando: {e}")
        return False
    
    # Test 2: Minijuegos
    print("2. ✅ Probando minijuegos...")
    try:
        scene_data = {
            "sceneId": 1,
            "decisions": [
                {"skill": "Toma de decisiones", "level": "Alto", "confidence": 0.85}
            ],
            "totalSteps": 5,
            "totalTime": 180,
            "averageConfidence": 0.75,
            "emotionalTrend": ["positivo"],
            "accessibilityUsed": False
        }
        
        response = requests.post(f"{BACKEND_URL}/api/logs/scene", json=scene_data)
        if response.status_code == 200:
            print("   Minijuegos funcionando correctamente")
        else:
            print(f"   ❌ Error: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Error en minijuegos: {e}")
        return False
    
    # Test 3: Análisis de CV
    print("3. ✅ Probando análisis de CV...")
    try:
        # Crear PDF simple
        from reportlab.pdfgen import canvas
        from io import BytesIO
        
        buffer = BytesIO()
        p = canvas.Canvas(buffer)
        p.drawString(100, 750, "CV TEST - Desarrolladora Frontend")
        p.drawString(100, 730, "React, TypeScript, JavaScript")
        p.drawString(100, 710, "5 años de experiencia")
        p.save()
        
        pdf_content = buffer.getvalue()
        buffer.close()
        
        # Guardar temporalmente
        with open("test_cv_final.pdf", "wb") as f:
            f.write(pdf_content)
        
        # Test de análisis
        user_data = {
            'userId': 'test-final',
            'fullName': 'Ana García',
            'softSkills': json.dumps([
                {"skill": "Comunicación", "level": "Alto", "confidence": 0.8}
            ]),
            'jobPreferences': json.dumps({
                "areas": ["Desarrollo Frontend"],
                "needs": ["Trabajo remoto"],
                "workMode": "remoto"
            }),
            'completedGames': json.dumps([1])
        }
        
        with open("test_cv_final.pdf", "rb") as f:
            files = {'file': ('test_cv_final.pdf', f, 'application/pdf')}
            response = requests.post(
                f"{BACKEND_URL}/api/pdf/analyze-cv", 
                files=files, 
                data=user_data
            )
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Análisis exitoso - Fortalezas: {len(data.get('strengths', []))}")
        else:
            print(f"   ❌ Error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error en análisis CV: {e}")
        return False
    finally:
        import os
        if os.path.exists("test_cv_final.pdf"):
            os.remove("test_cv_final.pdf")
    
    # Test 4: Generación de Informe
    print("4. ✅ Probando generación de informe...")
    try:
        report_data = {
            "userId": "test-final",
            "fullName": "Ana García",
            "softSkills": [
                {"skill": "Toma de decisiones", "level": "Alto", "confidence": 0.85, "score": 85},
                {"skill": "Comunicación", "level": "Medio", "confidence": 0.65, "score": 65}
            ],
            "cvAnalysis": {
                "strengths": ["Experiencia técnica sólida"],
                "weaknesses": ["Falta experiencia en gestión"],
                "feedback": "CV bien estructurado",
                "skills": ["React", "JavaScript"]
            },
            "jobPreferences": {
                "areas": ["Desarrollo Frontend"],
                "needs": ["Trabajo remoto"],
                "workMode": "remoto",
                "availability": "completa",
                "willingToRelocate": False,
                "hasDisabilityCert": False
            },
            "completedGames": [1, 2],
            "logs": []
        }
        
        response = requests.post(f"{BACKEND_URL}/api/logs/report", json=report_data)
        if response.status_code == 200:
            data = response.json()
            print(f"   Informe generado - Puntuación: {data.get('employabilityScore', 'N/A')}")
        else:
            print(f"   ❌ Error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error en informe: {e}")
        return False
    
    print("\n🎉 ¡TODAS LAS FUNCIONALIDADES CRÍTICAS FUNCIONAN!")
    print("=" * 50)
    print("✅ Backend operativo")
    print("✅ Minijuegos funcionando")
    print("✅ Análisis de CV con IA")
    print("✅ Generación de informes")
    print("\n🔗 URLs disponibles:")
    print(f"   Backend: {BACKEND_URL}")
    print(f"   API Docs: {BACKEND_URL}/docs")
    
    return True

if __name__ == "__main__":
    test_critical_functionality() 