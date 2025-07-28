#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de prueba para verificar la configuración de Azure OpenAI
"""

import os
from dotenv import load_dotenv
from openai import AzureOpenAI

def test_azure_openai_config():
    """Prueba la configuración de Azure OpenAI"""
    
    print("🔍 Verificando configuración de Azure OpenAI...")
    
    # Cargar variables de entorno
    load_dotenv()
    
    # Obtener variables
    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")
    api_version = os.getenv("AZURE_OPENAI_API_VERSION")
    
    print(f"📋 Variables de entorno:")
    print(f"  API_KEY: {'✅ Configurado' if api_key else '❌ No configurado'}")
    print(f"  ENDPOINT: {'✅ Configurado' if endpoint else '❌ No configurado'}")
    print(f"  DEPLOYMENT: {'✅ Configurado' if deployment else '❌ No configurado'}")
    print(f"  API_VERSION: {'✅ Configurado' if api_version else '❌ No configurado'}")
    
    # Verificar si todas las variables están configuradas
    if not all([api_key, endpoint, deployment, api_version]):
        print("\n❌ Faltan variables de entorno.")
        print("💡 Para configurar Azure OpenAI:")
        print("   1. Copia env.example como .env")
        print("   2. Edita .env con tus credenciales de Azure OpenAI")
        print("   3. Reinicia el servidor")
        return False
    
    try:
        # Crear cliente
        client = AzureOpenAI(
            api_key=api_key,
            api_version=api_version,
            azure_endpoint=endpoint
        )
        print("\n✅ Cliente Azure OpenAI creado correctamente")
        
        # Probar conexión con una llamada simple
        print("🧪 Probando conexión...")
        response = client.chat.completions.create(
            model=deployment,
            messages=[{"role": "user", "content": "Hola, esto es una prueba."}],
            max_tokens=10
        )
        
        if response.choices[0].message.content:
            print("✅ Conexión exitosa con Azure OpenAI")
            print("✅ Configuración correcta")
            return True
        else:
            print("❌ Respuesta vacía de Azure OpenAI")
            return False
            
    except Exception as e:
        print(f"❌ Error conectando con Azure OpenAI: {str(e)}")
        print("\n💡 Posibles soluciones:")
        print("   - Verifica que las credenciales sean correctas")
        print("   - Verifica que el deployment exista y esté activo")
        print("   - Verifica que el endpoint sea correcto")
        print("   - Verifica que tengas acceso al recurso de Azure OpenAI")
        return False

def test_cv_analysis():
    """Prueba el análisis de CV"""
    
    print("\n🔍 Verificando análisis de CV...")
    
    try:
        from cv_analyzer import extract_pdf_info
        
        # Crear un PDF de prueba simple
        import io
        from reportlab.pdfgen import canvas
        
        # Crear PDF de prueba
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer)
        p.drawString(100, 750, "CV de Prueba")
        p.drawString(100, 700, "Nombre: Juan Pérez")
        p.drawString(100, 650, "Experiencia: Desarrollador Python")
        p.drawString(100, 600, "Habilidades: Python, JavaScript, SQL")
        p.save()
        
        pdf_content = buffer.getvalue()
        
        # Probar análisis
        result = extract_pdf_info(pdf_content)
        
        if result.get("error"):
            print(f"❌ Error en análisis de CV: {result['error']}")
            return False
        else:
            print("✅ Análisis de CV funcionando correctamente")
            print(f"   Texto extraído: {len(result.get('raw_text', ''))} caracteres")
            return True
            
    except Exception as e:
        print(f"❌ Error en análisis de CV: {str(e)}")
        return False

def main():
    """Función principal"""
    
    print("🚀 Iniciando pruebas de configuración...\n")
    
    # Probar configuración de Azure OpenAI
    azure_ok = test_azure_openai_config()
    
    # Probar análisis de CV
    cv_ok = test_cv_analysis()
    
    print("\n" + "="*50)
    print("📊 RESUMEN DE PRUEBAS")
    print("="*50)
    
    if azure_ok and cv_ok:
        print("✅ TODO FUNCIONANDO CORRECTAMENTE")
        print("🎉 La aplicación debería funcionar sin errores")
    elif azure_ok and not cv_ok:
        print("⚠️ Azure OpenAI configurado pero análisis de CV con problemas")
        print("💡 Revisa las dependencias del análisis de CV")
    elif not azure_ok and cv_ok:
        print("⚠️ Análisis de CV funciona pero Azure OpenAI no configurado")
        print("💡 Configura Azure OpenAI para análisis completo de CV")
    else:
        print("❌ Problemas en la configuración")
        print("💡 Revisa la configuración y las dependencias")
    
    print("\n💡 Para más información, consulta CONFIGURAR_AZURE_OPENAI.md")

if __name__ == "__main__":
    main() 