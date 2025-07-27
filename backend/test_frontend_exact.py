#!/usr/bin/env python3
"""
Script para simular exactamente la petición del frontend y diagnosticar el problema
"""

import os
import sys
import json
import requests
from pathlib import Path

def test_exact_frontend_request():
    """Simula exactamente la petición que envía el frontend"""
    print("🔍 Simulando petición exacta del frontend...")
    
    # URL del endpoint
    url = "http://localhost:8000/api/informe-ia"
    
    # Datos exactos que envía el frontend (según el log)
    exact_data = {
        "userId": "user-ester-2025",
        "fullName": "Esther Pérez",
        "completedGames": [
            "decision-making", 
            "analytical-thinking", 
            "creativity", 
            "social-influence", 
            "curiosity-learning"
        ],
        "cvAnalysis": {
            "strengths": [],
            "weaknesses": [],
            "feedback": "No se pudo analizar completamente el CV",
            "structure": "regular",
            "coherence": "regular",
            "experience": "regular",
            "skills": [],
            "education": [],
            "alerts": ["Error en el análisis del CV"]
        },
        "fullName": "Esther Pérez",
        "jobPreferences": {
            "areas": ["grabadora de datos"],
            "needs": ["Necesito flexibilidad horaria"],
            "workMode": "remoto"
        },
        "logs": [],
        "softSkills": [
            {
                "skill": "Toma de decisiones",
                "score": 40,
                "level": "Bajo",
                "confidence": 40
            }
        ]
    }
    
    try:
        print("📤 Enviando petición exacta del frontend...")
        response = requests.post(
            url,
            json=exact_data,
            headers={
                'Content-Type': 'application/json',
                'Accept': '*/*',
                'Accept-Encoding': 'gzip, deflate, br, zstd',
                'Accept-Language': 'es-ES,es;q=0.9',
                'Connection': 'keep-alive',
                'Origin': 'http://localhost:3005',
                'Referer': 'http://localhost:3005/',
                'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Mobile Safari/537.36'
            },
            timeout=120
        )
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📊 Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Petición exitosa")
            
            if 'report' in result and 'informeProfesional' in result['report']:
                informe = result['report']['informeProfesional']
                print(f"📄 Longitud del informe: {len(informe)} caracteres")
                
                # Verificar si el informe menciona el problema del CV
                if "No se pudo analizar completamente el CV" in informe:
                    print("⚠️ El informe menciona el problema del CV")
                else:
                    print("✅ El informe no menciona el problema del CV")
                
                # Verificar si el informe incluye datos de las soft skills
                if "Toma de decisiones" in informe:
                    print("✅ El informe incluye datos de soft skills")
                else:
                    print("⚠️ El informe no incluye datos de soft skills")
                
                return True
            else:
                print("❌ No se generó el informe profesional")
                print(f"Respuesta: {result}")
                return False
        else:
            print(f"❌ Error en petición: {response.status_code}")
            print(f"Respuesta: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ No se pudo conectar al servidor")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

def test_cv_analysis_step():
    """Prueba el paso de análisis de CV para verificar si se está ejecutando"""
    print("\n🔍 Verificando paso de análisis de CV...")
    
    # Buscar un archivo PDF de prueba
    pdf_files = list(Path('.').glob('*.pdf'))
    if not pdf_files:
        print("❌ No se encontraron archivos PDF para probar")
        return False
    
    test_pdf = pdf_files[0]
    print(f"📄 Usando archivo: {test_pdf}")
    
    # URL del endpoint de análisis de CV
    url = "http://localhost:8000/api/pdf/analyze-cv"
    
    # Datos que debería enviar el frontend para análisis de CV
    form_data = {
        'userId': 'user-ester-2025',
        'fullName': 'Esther Pérez',
        'softSkills': json.dumps([
            {'skill': 'Toma de decisiones', 'score': 40, 'level': 'Bajo', 'confidence': 40}
        ]),
        'jobPreferences': json.dumps({
            'areas': ['grabadora de datos'],
            'needs': ['Necesito flexibilidad horaria'],
            'workMode': 'remoto'
        }),
        'completedGames': json.dumps(['decision-making', 'analytical-thinking'])
    }
    
    try:
        with open(test_pdf, 'rb') as f:
            files = {'file': (test_pdf.name, f, 'application/pdf')}
            
            print("📤 Enviando archivo para análisis...")
            response = requests.post(url, files=files, data=form_data, timeout=60)
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Análisis de CV exitoso")
            print(f"📊 Datos extraídos: {len(result)} campos")
            
            # Verificar que se extrajeron datos reales
            if result.get('strengths') or result.get('weaknesses') or result.get('skills'):
                print("✅ Se extrajeron datos reales del CV")
                return result
            else:
                print("⚠️ No se extrajeron datos significativos del CV")
                return False
        else:
            print(f"❌ Error en análisis de CV: {response.status_code}")
            print(f"Respuesta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

def test_complete_flow_with_real_cv():
    """Prueba el flujo completo con datos reales del CV"""
    print("\n🔄 Probando flujo completo con datos reales del CV...")
    
    # 1. Obtener análisis real del CV
    cv_analysis = test_cv_analysis_step()
    if not cv_analysis:
        print("❌ No se pudo obtener análisis del CV")
        return False
    
    # 2. Generar informe con datos reales del CV
    url = "http://localhost:8000/api/informe-ia"
    
    # Usar los datos reales del CV en lugar de los vacíos
    real_data = {
        "userId": "user-ester-2025",
        "fullName": "Esther Pérez",
        "completedGames": [
            "decision-making", 
            "analytical-thinking", 
            "creativity", 
            "social-influence", 
            "curiosity-learning"
        ],
        "cvAnalysis": cv_analysis,  # Usar datos reales del CV
        "jobPreferences": {
            "areas": ["grabadora de datos"],
            "needs": ["Necesito flexibilidad horaria"],
            "workMode": "remoto"
        },
        "logs": [],
        "softSkills": [
            {
                "skill": "Toma de decisiones",
                "score": 40,
                "level": "Bajo",
                "confidence": 40
            }
        ]
    }
    
    try:
        print("📤 Generando informe con datos reales del CV...")
        response = requests.post(
            url,
            json=real_data,
            headers={'Content-Type': 'application/json'},
            timeout=120
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Informe generado con datos reales del CV")
            
            if 'report' in result and 'informeProfesional' in result['report']:
                informe = result['report']['informeProfesional']
                print(f"📄 Longitud del informe: {len(informe)} caracteres")
                
                # Verificar que el informe no mencione el problema
                if "No se pudo analizar completamente el CV" not in informe:
                    print("✅ El informe no menciona el problema del CV")
                    return True
                else:
                    print("⚠️ El informe aún menciona el problema del CV")
                    return False
            else:
                print("❌ No se generó el informe profesional")
                return False
        else:
            print(f"❌ Error generando informe: {response.status_code}")
            print(f"Respuesta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

def main():
    """Función principal"""
    print("🧪 Iniciando diagnóstico del problema del frontend...")
    print("=" * 70)
    
    tests = [
        ("Petición Exacta del Frontend", test_exact_frontend_request),
        ("Flujo Completo con CV Real", test_complete_flow_with_real_cv)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*25} {test_name} {'='*25}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Error inesperado en {test_name}: {e}")
            results.append((test_name, False))
    
    # Resumen
    print(f"\n{'='*70}")
    print("📊 RESUMEN DEL DIAGNÓSTICO")
    print("=" * 70)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASÓ" if result else "❌ FALLÓ"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nResultado: {passed}/{len(results)} pruebas pasaron")
    
    if passed == len(results):
        print("🎉 El problema está identificado y solucionado!")
    else:
        print("⚠️ Se identificó el problema. Revisa los errores anteriores.")
    
    return passed == len(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 