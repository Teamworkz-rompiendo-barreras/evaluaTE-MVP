#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de prueba para verificar que el endpoint /api/pdf/analyze-cv actualizado
funciona correctamente con el CV real y utiliza las funciones avanzadas de cv_analyzer.
"""

import requests
import json
import os
from pathlib import Path

def test_cv_analysis_endpoint():
    """Prueba el endpoint de análisis de CV con el archivo real"""
    
    # Configuración
    base_url = "http://localhost:8000"
    endpoint = "/api/pdf/analyze-cv"
    cv_file_path = "cv_prueba.pdf"
    
    # Verificar que el archivo existe
    if not os.path.exists(cv_file_path):
        print(f"❌ Error: No se encuentra el archivo {cv_file_path}")
        return False
    
    print(f"📄 Probando análisis de CV con archivo: {cv_file_path}")
    
    # Datos de prueba
    test_data = {
        "userId": "test_user_123",
        "fullName": "Usuario de Prueba",
        "softSkills": json.dumps([
            {
                "skill": "Comunicación",
                "score": 75,
                "level": "medio",
                "confidence": 80
            },
            {
                "skill": "Trabajo en equipo",
                "score": 85,
                "level": "alto",
                "confidence": 90
            }
        ]),
        "jobPreferences": json.dumps({
            "areas": ["Desarrollo de software", "Análisis de datos"],
            "needs": ["Flexibilidad horaria", "Trabajo remoto"],
            "workMode": "remoto",
            "availability": "completa",
            "willingToRelocate": False,
            "hasDisabilityCert": False
        }),
        "completedGames": json.dumps(["juego1", "juego2"])
    }
    
    try:
        # Preparar el archivo para envío
        with open(cv_file_path, 'rb') as f:
            files = {'file': (cv_file_path, f, 'application/pdf')}
            
            print("🔄 Enviando solicitud al endpoint...")
            
            # Realizar la solicitud
            response = requests.post(
                f"{base_url}{endpoint}",
                files=files,
                data=test_data,
                timeout=60  # Timeout más largo para procesamiento de CV
            )
        
        print(f"📊 Código de respuesta: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Análisis de CV completado exitosamente!")
            
            # Mostrar resultados
            print("\n📋 RESULTADOS DEL ANÁLISIS:")
            print("=" * 50)
            
            if result.get("strengths"):
                print("💪 PUNTOS FUERTES:")
                for strength in result["strengths"]:
                    print(f"  • {strength}")
                print()
            
            if result.get("weaknesses"):
                print("⚠️ ÁREAS DE MEJORA:")
                for weakness in result["weaknesses"]:
                    print(f"  • {weakness}")
                print()
            
            if result.get("feedback"):
                print(f"💬 FEEDBACK: {result['feedback']}")
                print()
            
            if result.get("structure"):
                print(f"📐 ESTRUCTURA: {result['structure']}")
            
            if result.get("coherence"):
                print(f"🔗 COHERENCIA: {result['coherence']}")
            
            if result.get("experience"):
                print(f"💼 EXPERIENCIA: {result['experience']}")
            
            if result.get("skills"):
                print("🛠️ HABILIDADES TÉCNICAS:")
                for skill in result["skills"]:
                    print(f"  • {skill}")
                print()
            
            if result.get("education"):
                print("🎓 FORMACIÓN:")
                for edu in result["education"]:
                    print(f"  • {edu}")
                print()
            
            if result.get("alerts"):
                print("🚨 ALERTAS:")
                for alert in result["alerts"]:
                    print(f"  ⚠️ {alert}")
                print()
            
            # Verificar que el análisis es completo
            required_fields = ["strengths", "weaknesses", "feedback", "structure", "coherence", "experience"]
            missing_fields = [field for field in required_fields if not result.get(field)]
            
            if missing_fields:
                print(f"⚠️ Campos faltantes en el análisis: {missing_fields}")
            else:
                print("✅ Análisis completo con todos los campos requeridos")
            
            return True
            
        else:
            print(f"❌ Error en la respuesta: {response.status_code}")
            print(f"Detalle: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Error: No se puede conectar al servidor. Asegúrate de que esté ejecutándose en http://localhost:8000")
        return False
    except requests.exceptions.Timeout:
        print("❌ Error: Timeout en la solicitud. El procesamiento del CV tardó demasiado.")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {str(e)}")
        return False

def test_cv_analyzer_direct():
    """Prueba directa de cv_analyzer para comparar resultados"""
    
    print("\n" + "="*60)
    print("🔬 PRUEBA DIRECTA DE CV_ANALYZER")
    print("="*60)
    
    try:
        from cv_analyzer import extract_pdf_info
        
        cv_file_path = "cv_prueba.pdf"
        
        if not os.path.exists(cv_file_path):
            print(f"❌ Error: No se encuentra el archivo {cv_file_path}")
            return False
        
        print(f"📄 Analizando CV directamente con cv_analyzer...")
        
        with open(cv_file_path, 'rb') as f:
            pdf_buffer = f.read()
        
        result = extract_pdf_info(pdf_buffer)
        
        if result.get("error"):
            print(f"❌ Error en cv_analyzer: {result['error']}")
            return False
        
        print("✅ Análisis directo completado!")
        
        # Mostrar información extraída
        cv_info = result.get("cv_info", {})
        analysis = result.get("analysis", {})
        
        print(f"\n📊 INFORMACIÓN EXTRAÍDA:")
        print(f"  • Contacto: {len(cv_info.get('contacto', {}))} elementos")
        print(f"  • Software/Habilidades: {len(cv_info.get('software', []))} elementos")
        print(f"  • Experiencia: {len(cv_info.get('experiencia', []))} elementos")
        print(f"  • Educación: {len(cv_info.get('educacion', []))} elementos")
        print(f"  • Texto extraído: {len(result.get('raw_text', ''))} caracteres")
        
        if analysis:
            print(f"\n📋 ANÁLISIS ESTRUCTURADO:")
            print(f"  • Fortalezas: {len(analysis.get('strengths', []))} elementos")
            print(f"  • Debilidades: {len(analysis.get('weaknesses', []))} elementos")
            print(f"  • Alertas: {len(analysis.get('alerts', []))} elementos")
        
        return True
        
    except ImportError as e:
        print(f"❌ Error importando cv_analyzer: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ Error en análisis directo: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 INICIANDO PRUEBAS DE ANÁLISIS DE CV REAL")
    print("=" * 60)
    
    # Prueba 1: Análisis directo con cv_analyzer
    test1_success = test_cv_analyzer_direct()
    
    # Prueba 2: Endpoint actualizado
    test2_success = test_cv_analysis_endpoint()
    
    print("\n" + "="*60)
    print("📊 RESUMEN DE PRUEBAS")
    print("="*60)
    print(f"✅ Análisis directo cv_analyzer: {'EXITOSO' if test1_success else 'FALLIDO'}")
    print(f"✅ Endpoint /api/pdf/analyze-cv: {'EXITOSO' if test2_success else 'FALLIDO'}")
    
    if test1_success and test2_success:
        print("\n🎉 ¡TODAS LAS PRUEBAS EXITOSAS!")
        print("La aplicación puede analizar CVs reales incluyendo PDFs escaneados.")
    else:
        print("\n⚠️ Algunas pruebas fallaron. Revisa los errores anteriores.") 