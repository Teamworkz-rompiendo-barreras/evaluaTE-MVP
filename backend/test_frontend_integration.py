#!/usr/bin/env python3
"""
Script para simular la integración del frontend con el backend
y verificar que el análisis de CV funcione correctamente
"""

import os
import sys
import json
import requests
from pathlib import Path

def test_frontend_integration():
    """Simula exactamente lo que hace el frontend"""
    print("🔍 Simulando integración frontend-backend...")
    
    # Buscar un archivo PDF de prueba
    pdf_files = list(Path('.').glob('*.pdf'))
    if not pdf_files:
        print("❌ No se encontraron archivos PDF para probar")
        return False
    
    test_pdf = pdf_files[0]
    print(f"📄 Usando archivo: {test_pdf}")
    
    # URL del endpoint
    url = "http://localhost:8000/api/pdf/analyze-cv"
    
    # Simular exactamente los datos que envía el frontend
    form_data = {
        'userId': 'user-ester-2025',
        'fullName': 'Ester Pérez Ribada',
        'softSkills': json.dumps([]),
        'jobPreferences': json.dumps({}),
        'completedGames': json.dumps([])
    }
    
    try:
        # Enviar archivo y datos como lo hace el frontend
        with open(test_pdf, 'rb') as f:
            files = {'file': (test_pdf.name, f, 'application/pdf')}
            
            print("📤 Enviando petición (simulando frontend)...")
            response = requests.post(url, files=files, data=form_data, timeout=60)
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Integración frontend-backend exitosa")
            print(f"📊 Datos del CV extraídos: {len(result)} campos")
            
            # Verificar que los datos no estén vacíos
            if result.get('strengths') or result.get('weaknesses') or result.get('skills'):
                print("✅ El CV se analizó correctamente con datos reales")
                
                if result.get('strengths'):
                    print(f"✅ Fortalezas encontradas: {len(result['strengths'])}")
                if result.get('weaknesses'):
                    print(f"✅ Debilidades encontradas: {len(result['weaknesses'])}")
                if result.get('skills'):
                    print(f"✅ Habilidades encontradas: {len(result['skills'])}")
                if result.get('education'):
                    print(f"✅ Educación encontrada: {len(result['education'])}")
                
                return True
            else:
                print("⚠️ El CV se procesó pero no se extrajeron datos significativos")
                print(f"📊 Resultado: {result}")
                return False
        else:
            print(f"❌ Error en integración: {response.status_code}")
            print(f"Respuesta: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ No se pudo conectar al servidor. ¿Está ejecutándose?")
        print("Ejecuta: uvicorn main:app --reload --host 0.0.0.0 --port 8000")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

def test_complete_flow():
    """Prueba el flujo completo: CV -> Análisis -> Informe IA"""
    print("\n🔄 Probando flujo completo...")
    
    # 1. Analizar CV
    cv_analysis = test_frontend_integration()
    if not cv_analysis:
        return False
    
    # 2. Generar informe IA con los datos del CV
    print("\n📋 Generando informe IA con datos del CV...")
    
    url = "http://localhost:8000/api/informe-ia"
    
    # Datos de prueba con análisis de CV real
    test_data = {
        'userId': 'user-ester-2025',
        'fullName': 'Esther Pérez',
        'softSkills': [
            {'skill': 'Toma de decisiones', 'score': 40, 'level': 'Bajo', 'confidence': 40}
        ],
        'cvAnalysis': {
            'strengths': ['Experiencia técnica sólida', 'Conocimientos en programación'],
            'weaknesses': ['Falta de experiencia en gestión de equipos'],
            'feedback': 'CV bien estructurado con experiencia técnica relevante',
            'structure': 'buena',
            'coherence': 'buena',
            'experience': 'regular',
            'skills': ['Python', 'JavaScript', 'SQL', 'React'],
            'education': ['Ingeniería Informática', 'Certificación en Desarrollo Web'],
            'alerts': []
        },
        'jobPreferences': {
            'areas': ['grabadora de datos', 'desarrollo de software'],
            'needs': ['Necesito flexibilidad horaria'],
            'workMode': 'remoto'
        },
        'completedGames': ['decision-making', 'analytical-thinking'],
        'logs': []
    }
    
    try:
        response = requests.post(
            url, 
            json=test_data, 
            headers={'Content-Type': 'application/json'},
            timeout=120
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Informe IA generado correctamente")
            
            if 'report' in result and 'informeProfesional' in result['report']:
                informe = result['report']['informeProfesional']
                print(f"📄 Longitud del informe: {len(informe)} caracteres")
                
                # Verificar que el informe contenga datos del CV
                cv_keywords = ['Python', 'JavaScript', 'SQL', 'React', 'Ingeniería Informática']
                found_keywords = [kw for kw in cv_keywords if kw in informe]
                
                if found_keywords:
                    print(f"✅ El informe incluye datos del CV: {found_keywords}")
                    return True
                else:
                    print("⚠️ El informe no parece incluir datos específicos del CV")
                    return False
            else:
                print("❌ No se generó el informe profesional")
                return False
        else:
            print(f"❌ Error generando informe IA: {response.status_code}")
            print(f"Respuesta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

def main():
    """Función principal"""
    print("🧪 Iniciando pruebas de integración frontend-backend...")
    print("=" * 70)
    
    tests = [
        ("Integración Frontend-Backend", test_frontend_integration),
        ("Flujo Completo", test_complete_flow)
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
    print("📊 RESUMEN DE INTEGRACIÓN")
    print("=" * 70)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASÓ" if result else "❌ FALLÓ"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nResultado: {passed}/{len(results)} pruebas pasaron")
    
    if passed == len(results):
        print("🎉 ¡La integración frontend-backend funciona correctamente!")
        print("💡 El problema del CV debería estar resuelto.")
    else:
        print("⚠️ Algunas pruebas fallaron. Revisa los errores anteriores.")
    
    return passed == len(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 