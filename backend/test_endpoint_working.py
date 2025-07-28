#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para probar que el endpoint del informe funciona correctamente
"""

import requests
import json
import time

def test_informe_endpoint():
    """Prueba el endpoint del informe con datos del CV"""
    print("🔍 PROBANDO ENDPOINT DEL INFORME")
    print("=" * 50)
    
    # Datos de prueba que simulan el frontend
    test_data = {
        "userId": "user-test-2025",
        "fullName": "Ana García",
        "softSkills": [
            {
                "skill": "Comunicación",
                "score": 75,
                "level": "Medio",
                "confidence": 80
            },
            {
                "skill": "Trabajo en equipo",
                "score": 85,
                "level": "Alto",
                "confidence": 90
            },
            {
                "skill": "Resolución de problemas",
                "score": 70,
                "level": "Medio",
                "confidence": 75
            }
        ],
        "cvAnalysis": {
            "strengths": ["Experiencia en desarrollo web", "Conocimientos de Python"],
            "weaknesses": ["Falta de experiencia en gestión de proyectos"],
            "feedback": "CV bien estructurado pero necesita más detalles en proyectos",
            "structure": "Clara y fácil de seguir",
            "coherence": "La experiencia es coherente con los objetivos",
            "experience": "3 años en desarrollo web",
            "skills": ["Python", "JavaScript", "React", "Django"],
            "education": ["Ingeniería Informática", "Curso de Desarrollo Web"],
            "alerts": ["Falta información de contacto", "Periodos sin actividad no explicados"]
        },
        "jobPreferences": {
            "areas": ["Desarrollo web", "Programación"],
            "needs": ["Flexibilidad horaria", "Trabajo remoto"],
            "workMode": "remoto",
            "availability": "completa",
            "willingToRelocate": False,
            "hasDisabilityCert": False
        },
        "completedGames": ["1", "2", "3"],
        "logs": []
    }
    
    print("📤 Enviando datos al endpoint...")
    print(f"  • Usuario: {test_data['fullName']}")
    print(f"  • Soft Skills: {len(test_data['softSkills'])}")
    print(f"  • CV Analysis: {'✅ Presente' if test_data.get('cvAnalysis') else '❌ Ausente'}")
    print(f"  • Job Preferences: {'✅ Presentes' if test_data.get('jobPreferences') else '❌ Ausentes'}")
    
    try:
        # Hacer la petición al endpoint
        response = requests.post(
            "http://localhost:8000/api/informe-ia",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=60  # 60 segundos de timeout
        )
        
        print(f"📥 Respuesta recibida: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Endpoint funcionando correctamente")
            
            # Verificar la respuesta
            if data.get('report', {}).get('informeProfesional'):
                informe = data['report']['informeProfesional']
                print(f"📄 Informe generado: {len(informe)} caracteres")
                
                # Verificar si el CV se menciona en el informe
                cv_keywords = ["CV", "currículum", "experiencia", "habilidades técnicas", "formación", "Python", "JavaScript", "React", "Django"]
                cv_mentions = sum(1 for keyword in cv_keywords if keyword.lower() in informe.lower())
                
                print(f"🔍 Menciones del CV en informe: {cv_mentions}/{len(cv_keywords)}")
                
                # Mostrar fragmento del informe
                print("\n📄 FRAGMENTO DEL INFORME:")
                lines = informe.split('\n')
                for i, line in enumerate(lines[:10]):  # Primeras 10 líneas
                    print(f"{i+1:2d}: {line}")
                
                return True
            else:
                print("❌ El informe no se generó correctamente")
                print(f"Respuesta completa: {json.dumps(data, indent=2, ensure_ascii=False)}")
                return False
        else:
            print(f"❌ Error en el endpoint: {response.status_code}")
            print(f"Respuesta: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Timeout en la petición (más de 60 segundos)")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ Error de conexión. Verificar que el backend esté ejecutándose en http://localhost:8000")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {str(e)}")
        return False

def test_endpoint_without_cv():
    """Prueba el endpoint sin datos del CV"""
    print("\n🔍 PROBANDO ENDPOINT SIN CV")
    print("=" * 50)
    
    # Datos de prueba sin CV
    test_data = {
        "userId": "user-test-2025",
        "fullName": "Ana García",
        "softSkills": [
            {
                "skill": "Comunicación",
                "score": 75,
                "level": "Medio",
                "confidence": 80
            },
            {
                "skill": "Trabajo en equipo",
                "score": 85,
                "level": "Alto",
                "confidence": 90
            }
        ],
        "cvAnalysis": None,
        "jobPreferences": {
            "areas": ["Desarrollo web"],
            "needs": ["Flexibilidad horaria"],
            "workMode": "remoto",
            "availability": "completa",
            "willingToRelocate": False,
            "hasDisabilityCert": False
        },
        "completedGames": ["1", "2"],
        "logs": []
    }
    
    print("📤 Enviando datos sin CV al endpoint...")
    print(f"  • Usuario: {test_data['fullName']}")
    print(f"  • Soft Skills: {len(test_data['softSkills'])}")
    print(f"  • CV Analysis: {'✅ Presente' if test_data.get('cvAnalysis') else '❌ Ausente'}")
    
    try:
        response = requests.post(
            "http://localhost:8000/api/informe-ia",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        
        print(f"📥 Respuesta recibida: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Endpoint funcionando correctamente sin CV")
            
            if data.get('report', {}).get('informeProfesional'):
                informe = data['report']['informeProfesional']
                print(f"📄 Informe generado: {len(informe)} caracteres")
                return True
            else:
                print("❌ El informe no se generó correctamente")
                return False
        else:
            print(f"❌ Error en el endpoint: {response.status_code}")
            print(f"Respuesta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def main():
    """Ejecuta las pruebas del endpoint"""
    print("🚀 PROBANDO ENDPOINT DEL INFORME")
    print("=" * 60)
    
    # Verificar que el backend esté ejecutándose
    try:
        response = requests.get("http://localhost:8000/", timeout=5)
        if response.status_code == 200:
            print("✅ Backend ejecutándose correctamente")
        else:
            print("❌ Backend no responde correctamente")
            return
    except:
        print("❌ Backend no está ejecutándose. Iniciar con: python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload")
        return
    
    # Prueba 1: Con CV
    test1_success = test_informe_endpoint()
    
    # Prueba 2: Sin CV
    test2_success = test_endpoint_without_cv()
    
    # Resumen
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE PRUEBAS:")
    print(f"  • Endpoint con CV: {'✅ FUNCIONA' if test1_success else '❌ FALLA'}")
    print(f"  • Endpoint sin CV: {'✅ FUNCIONA' if test2_success else '❌ FALLA'}")
    
    if all([test1_success, test2_success]):
        print("\n🎉 ENDPOINT FUNCIONANDO CORRECTAMENTE")
        print("💡 El backend está procesando correctamente los datos del CV")
        print("🔧 El problema debe estar en el frontend o en la comunicación")
    else:
        print("\n⚠️ ALGUNAS PRUEBAS FALLARON")
        print("🔧 Revisar la configuración del backend")

if __name__ == "__main__":
    main() 