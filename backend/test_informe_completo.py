#!/usr/bin/env python3
"""
Script de prueba para el flujo completo: análisis de CV + generación de informe con IA
"""

import requests
import json
import os

def test_complete_flow():
    print("🔍 Probando flujo completo: CV + Informe IA...")
    print("=" * 60)
    
    # Verificar que el archivo existe
    cv_path = "cv_prueba.pdf"
    if not os.path.exists(cv_path):
        print(f"❌ Error: No se encuentra el archivo {cv_path}")
        return
    
    print(f"✅ Archivo encontrado: {cv_path}")
    
    # Paso 1: Analizar el CV
    print("\n📄 PASO 1: Analizando CV...")
    cv_analysis = analyze_cv(cv_path)
    if not cv_analysis:
        return
    
    # Paso 2: Generar informe con IA
    print("\n🤖 PASO 2: Generando informe con IA...")
    generate_ia_report(cv_analysis)

def analyze_cv(cv_path):
    """Analiza el CV usando la API del backend"""
    url = "http://localhost:8000/api/analyze-cv"
    
    try:
        with open(cv_path, 'rb') as f:
            files = {'cv': (cv_path, f, 'application/pdf')}
            response = requests.post(url, files=files)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Análisis de CV exitoso!")
            print(f"  Estructura: {result.get('structure', 'N/A')}")
            print(f"  Coherencia: {result.get('coherence', 'N/A')}")
            print(f"  Experiencia: {result.get('experience', 'N/A')}")
            print(f"  Habilidades: {len(result.get('skills', []))}")
            return result
        else:
            print(f"❌ Error en análisis de CV: {response.status_code}")
            print(f"Respuesta: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error analizando CV: {e}")
        return None

def generate_ia_report(cv_analysis):
    """Genera el informe final usando IA"""
    url = "http://localhost:8000/api/informe-ia"
    
    # Datos de prueba para simular un usuario completo
    test_data = {
        "preferences": {
            "jobPreferences": "Desarrollo Full Stack",
            "workMode": "híbrido",
            "availability": "completa",
            "startDate": "inmediata",
            "relocate": True,
            "cert": True
        },
        "minigames": {
            "completedGames": ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"],
            "gameResults": {
                "resolucion_problemas": 85,
                "comunicacion_asertiva": 72,
                "trabajo_equipo": 88,
                "adaptabilidad": 79,
                "liderazgo": 65
            }
        },
        "cvAnalysis": {
            "structure": cv_analysis.get("structure", "regular"),
            "coherence": cv_analysis.get("coherence", "regular"),
            "experience": cv_analysis.get("experience", "regular"),
            "skills": cv_analysis.get("skills", []),
            "strengths": ["Experiencia técnica sólida", "Capacidad de aprendizaje"],
            "weaknesses": ["Comunicación escrita", "Gestión de proyectos"],
            "feedback": "CV con buena base técnica pero necesita mejorar la presentación"
        }
    }
    
    try:
        print("📤 Enviando datos para generar informe con IA...")
        response = requests.post(url, json=test_data, headers={'Content-Type': 'application/json'})
        
        print(f"📥 Respuesta del servidor: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Informe generado exitosamente!")
            print("\n📋 Informe de IA:")
            print("=" * 50)
            print(result.get('informe', 'Informe no disponible'))
            print("=" * 50)
            
            # Guardar el informe en un archivo
            with open('informe_generado.txt', 'w', encoding='utf-8') as f:
                f.write(result.get('informe', 'Informe no disponible'))
            print("\n💾 Informe guardado en 'informe_generado.txt'")
            
        else:
            print(f"❌ Error generando informe: {response.status_code}")
            print(f"Respuesta: {response.text}")
            
    except Exception as e:
        print(f"❌ Error generando informe: {e}")

if __name__ == "__main__":
    test_complete_flow() 