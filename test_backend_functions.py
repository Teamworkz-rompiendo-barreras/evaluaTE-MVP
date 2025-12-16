#!/usr/bin/env python3
# test_backend_functions.py
# Script para probar las funciones del backend y identificar el error

import sys
import os
import pathlib

# Agregar el directorio backend al path (para Pyright/ejecución local)
ROOT_DIR = pathlib.Path(__file__).resolve().parent
BACKEND_DIR = ROOT_DIR / "backend"
sys.path.insert(0, str(ROOT_DIR))
sys.path.insert(0, str(BACKEND_DIR))

def test_new_report_schema():
    """Prueba las funciones del nuevo esquema de reportes"""
    print("🧪 Probando funciones del nuevo esquema de reportes...\n")
    
    try:
        # Importar las funciones
        from backend import new_report_schema
        create_default_report = new_report_schema.create_default_report
        convert_old_format_to_new = new_report_schema.convert_old_format_to_new
        NewReportSchema = new_report_schema.NewReportSchema
        print("✅ Importación exitosa")
        
        # Crear datos de prueba
        test_data = {
            "fullName": "Usuario Test",
            "softSkills": [
                {"skill": "Comunicación", "score": 85, "level": "alto", "confidence": 90},
                {"skill": "Trabajo en equipo", "score": 78, "level": "medio", "confidence": 85}
            ],
            "cvAnalysis": {
                "structure": "excelente",
                "coherence": "buena",
                "feedback": "CV muy bien estructurado"
            },
            "jobPreferences": {
                "areas": ["Desarrollo Web"],
                "workMode": "remoto",
                "hasDisabilityCert": False
            }
        }
        
        print("📊 Datos de prueba creados")
        print(f"  - Nombre: {test_data['fullName']}")
        print(f"  - Soft Skills: {len(test_data['softSkills'])} habilidades")
        print(f"  - CV Analysis: {test_data['cvAnalysis']['structure']}")
        print(f"  - Job Preferences: {test_data['jobPreferences']['areas']}")
        
        # Probar create_default_report
        print("\n🔄 Probando create_default_report...")
        try:
            report = create_default_report(
                full_name=test_data["fullName"],
                soft_skills=test_data["softSkills"],
                cv_analysis=test_data["cvAnalysis"],
                job_preferences=test_data["jobPreferences"]
            )
            print("✅ create_default_report ejecutado exitosamente")
            print(f"  - Tipo de retorno: {type(report)}")
            print(f"  - Nombre: {report.personal_data.name}")
            print(f"  - Fortalezas: {len(report.strengths)} fortalezas")
            print(f"  - Plan de acción: {len(report.action_plan.short_term)} acciones corto plazo")
            
            # Probar conversión a diccionario
            print("\n🔄 Probando conversión a diccionario...")
            try:
                report_dict = report.dict()
                print("✅ Conversión a diccionario exitosa")
                print(f"  - Claves principales: {list(report_dict.keys())[:5]}...")
                print(f"  - Tamaño del diccionario: {len(report_dict)} campos")
            except Exception as e:
                print(f"❌ Error en conversión a diccionario: {e}")
                return False
                
        except Exception as e:
            print(f"❌ Error en create_default_report: {e}")
            import traceback
            traceback.print_exc()
            return False
            
        # Probar convert_old_format_to_new
        print("\n🔄 Probando convert_old_format_to_new...")
        try:
            old_format_data = {
                "report": {
                    "fullName": "Usuario Antiguo",
                    "resumen_ejecutivo": "Resumen del formato antiguo"
                },
                "recommendations": ["Recomendación 1", "Recomendación 2"],
                "employabilityScore": 75
            }
            
            converted_report = convert_old_format_to_new(old_format_data)
            print("✅ convert_old_format_to_new ejecutado exitosamente")
            print(f"  - Nombre convertido: {converted_report.personal_data.name}")
            print(f"  - Fortalezas convertidas: {len(converted_report.strengths)}")
            
        except Exception as e:
            print(f"❌ Error en convert_old_format_to_new: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        print("\n🎉 ¡Todas las pruebas pasaron exitosamente!")
        return True
        
    except Exception as e:
        print(f"❌ Error general: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_endpoint_logic():
    """Prueba la lógica del endpoint"""
    print("\n🧪 Probando lógica del endpoint...\n")
    
    try:
        # Simular la lógica del endpoint
        from backend import new_report_schema
        create_default_report = new_report_schema.create_default_report
        
        # Simular request
        req = type('Request', (), {
            'fullName': 'Usuario Test',
            'softSkills': [],
            'cvAnalysis': {},
            'jobPreferences': {},
            'userId': 'test-123'
        })()
        
        print("📤 Request simulado creado")
        
        # Probar la lógica del endpoint
        try:
            new_report = create_default_report(
                full_name=req.fullName or "Usuario",
                soft_skills=req.softSkills or [],
                cv_analysis=req.cvAnalysis or {},
                job_preferences=req.jobPreferences or {}
            )
            print("✅ Lógica del endpoint ejecutada exitosamente")
            
            # Probar conversión a JSON
            try:
                report_dict = new_report.dict()
                print("✅ Conversión a JSON exitosa")
                return True
            except Exception as e:
                print(f"❌ Error en conversión a JSON: {e}")
                return False
                
        except Exception as e:
            print(f"❌ Error en la lógica del endpoint: {e}")
            import traceback
            traceback.print_exc()
            return False
            
    except Exception as e:
        print(f"❌ Error general en test del endpoint: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Iniciando pruebas del backend...\n")
    
    # Probar funciones del esquema
    schema_ok = test_new_report_schema()
    
    if schema_ok:
        # Probar lógica del endpoint
        endpoint_ok = test_endpoint_logic()
        
        if endpoint_ok:
            print("\n🎉 ¡Todas las pruebas pasaron! El backend debería funcionar correctamente.")
        else:
            print("\n❌ Hay un problema en la lógica del endpoint.")
    else:
        print("\n❌ Hay un problema en las funciones del esquema.")
    
    print("\n🔍 Revisa los errores anteriores para identificar el problema específico.")
