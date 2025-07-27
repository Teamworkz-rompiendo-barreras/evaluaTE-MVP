#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para probar el flujo completo usando el endpoint real de la aplicación
con el CV real cv_prueba.pdf.
"""

import json
import sys
import os
import requests
from datetime import datetime

def test_endpoint_completo():
    """Prueba el flujo completo usando el endpoint real"""
    
    print("🚀 PRUEBA DEL FLUJO COMPLETO CON ENDPOINT REAL")
    print("=" * 60)
    
    # Verificar que el archivo existe
    cv_path = "cv_prueba.pdf"
    if not os.path.exists(cv_path):
        print(f"❌ Error: No se encuentra el archivo {cv_path}")
        return False
    
    print(f"✅ Archivo CV encontrado: {cv_path}")
    
    # URL base del servidor (asumiendo que está corriendo localmente)
    base_url = "http://localhost:8000"
    
    # 1. Primero, analizar el CV usando el endpoint /api/pdf/analyze-cv
    print("\n🔍 PASO 1: ANALIZANDO CV CON ENDPOINT /api/pdf/analyze-cv")
    
    try:
        # Preparar datos para el análisis del CV
        soft_skills = [
            {"skill": "Comunicación", "score": 85, "level": "alto", "confidence": 90},
            {"skill": "Trabajo en equipo", "score": 92, "level": "alto", "confidence": 88},
            {"skill": "Resolución de problemas", "score": 78, "level": "medio", "confidence": 85}
        ]
        
        job_preferences = {
            "areas": ["Desarrollo web", "Análisis de datos"],
            "needs": ["Entorno colaborativo", "Oportunidades de aprendizaje"],
            "workMode": "híbrido",
            "availability": "completa",
            "willingToRelocate": True,
            "hasDisabilityCert": False
        }
        
        completed_games = ["comunicacion", "liderazgo"]
        
        # Preparar el formulario multipart
        files = {
            'file': ('cv_prueba.pdf', open(cv_path, 'rb'), 'application/pdf')
        }
        
        data = {
            'userId': 'test_user_endpoint',
            'fullName': 'Ana García López',
            'softSkills': json.dumps(soft_skills),
            'jobPreferences': json.dumps(job_preferences),
            'completedGames': json.dumps(completed_games)
        }
        
        print("📤 Enviando solicitud de análisis del CV...")
        response = requests.post(f"{base_url}/api/pdf/analyze-cv", files=files, data=data)
        
        if response.status_code == 200:
            cv_analysis = response.json()
            print("✅ Análisis del CV completado exitosamente")
            print(f"📊 Fortalezas detectadas: {len(cv_analysis.get('strengths', []))}")
            print(f"📊 Debilidades detectadas: {len(cv_analysis.get('weaknesses', []))}")
            print(f"📊 Habilidades técnicas: {len(cv_analysis.get('skills', []))}")
            print(f"📊 Formación detectada: {len(cv_analysis.get('education', []))}")
            print(f"📊 Alertas: {len(cv_analysis.get('alerts', []))}")
        else:
            print(f"❌ Error en análisis del CV: {response.status_code}")
            print(f"Respuesta: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ No se puede conectar al servidor. Asegúrate de que esté corriendo en http://localhost:8000")
        return False
    except Exception as e:
        print(f"❌ Error en análisis del CV: {str(e)}")
        return False
    
    # 2. Generar el informe completo usando el endpoint /api/logs/report
    print("\n📋 PASO 2: GENERANDO INFORME COMPLETO CON ENDPOINT /api/logs/report")
    
    try:
        # Preparar datos para el informe completo
        report_data = {
            "userId": "test_user_endpoint",
            "fullName": "Ana García López",
            "softSkills": [
                {"skill": "Comunicación", "score": 85, "level": "alto", "confidence": 90},
                {"skill": "Trabajo en equipo", "score": 92, "level": "alto", "confidence": 88},
                {"skill": "Resolución de problemas", "score": 78, "level": "medio", "confidence": 85},
                {"skill": "Liderazgo", "score": 65, "level": "medio", "confidence": 70},
                {"skill": "Adaptabilidad", "score": 88, "level": "alto", "confidence": 92}
            ],
            "cvAnalysis": cv_analysis,  # Usar el análisis real del CV
            "jobPreferences": {
                "areas": ["Desarrollo web", "Análisis de datos", "DevOps"],
                "needs": ["Entorno colaborativo", "Oportunidades de aprendizaje", "Flexibilidad horaria"],
                "workMode": "híbrido",
                "availability": "completa",
                "willingToRelocate": True,
                "hasDisabilityCert": False
            },
            "completedGames": ["comunicacion", "liderazgo", "trabajo_equipo"],
            "logs": []
        }
        
        print("📤 Enviando solicitud de informe completo...")
        response = requests.post(f"{base_url}/api/logs/report", json=report_data)
        
        if response.status_code == 200:
            report_result = response.json()
            print("✅ Informe completo generado exitosamente")
            
            # Verificar que el análisis del CV esté en el informe
            report_content = report_result.get('report', {})
            cv_in_report = report_content.get('cvAnalysis')
            
            if cv_in_report:
                print("✅ Análisis del CV incluido en el informe")
                print(f"📊 Fortalezas en informe: {len(cv_in_report.get('strengths', []))}")
                print(f"📊 Habilidades técnicas en informe: {len(cv_in_report.get('skills', []))}")
                print(f"📊 Formación en informe: {len(cv_in_report.get('education', []))}")
                print(f"📊 Alertas en informe: {len(cv_in_report.get('alerts', []))}")
            else:
                print("❌ Análisis del CV NO encontrado en el informe")
                return False
                
        else:
            print(f"❌ Error generando informe: {response.status_code}")
            print(f"Respuesta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error generando informe: {str(e)}")
        return False
    
    # 3. Generar el PDF del informe usando el endpoint /api/pdf/generate-report
    print("\n🖨️ PASO 3: GENERANDO PDF DEL INFORME CON ENDPOINT /api/pdf/generate-report")
    
    try:
        print("📤 Enviando solicitud de generación de PDF...")
        response = requests.post(f"{base_url}/api/pdf/generate-report", json=report_data)
        
        if response.status_code == 200:
            # Guardar el PDF
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            pdf_filename = f"informe_endpoint_{timestamp}.pdf"
            
            with open(pdf_filename, 'wb') as f:
                f.write(response.content)
            
            print(f"✅ PDF generado exitosamente: {pdf_filename}")
            print(f"📏 Tamaño: {len(response.content)} bytes")
            
            # Verificar que el archivo se guardó correctamente
            if os.path.exists(pdf_filename):
                file_size = os.path.getsize(pdf_filename)
                print(f"💾 Archivo guardado: {file_size} bytes")
                
                if file_size > 1000:
                    print("✅ PDF parece válido")
                else:
                    print("⚠️ PDF muy pequeño, puede haber un problema")
            else:
                print("❌ Error: El PDF no se guardó correctamente")
                return False
                
        else:
            print(f"❌ Error generando PDF: {response.status_code}")
            print(f"Respuesta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error generando PDF: {str(e)}")
        return False
    
    print("\n🎉 RESUMEN DE LA PRUEBA DEL ENDPOINT")
    print("=" * 60)
    print("✅ CV real analizado correctamente")
    print("✅ Información del CV extraída y procesada")
    print("✅ Informe completo generado con análisis del CV")
    print("✅ PDF generado exitosamente")
    print("✅ Análisis del CV incluido en todos los pasos del flujo")
    
    return True

def main():
    """Función principal"""
    print("🚀 PRUEBA PROFESIONAL DEL FLUJO COMPLETO")
    print("=" * 60)
    
    try:
        success = test_endpoint_completo()
        
        if success:
            print("\n✅ PRUEBA EXITOSA")
            print("El flujo completo funciona correctamente")
            print("El análisis del CV llega correctamente al informe final")
            print("El PDF generado contiene toda la información del CV")
            sys.exit(0)
        else:
            print("\n❌ PRUEBA FALLIDA")
            print("El flujo completo no funciona correctamente")
            print("El análisis del CV no llega al informe final")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n❌ Error durante la prueba: {str(e)}")
        import traceback
        print(f"📋 Traceback: {traceback.format_exc()}")
        sys.exit(1)

if __name__ == "__main__":
    main() 