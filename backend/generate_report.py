# backend/generate_report.py

import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cargar variables de entorno
load_dotenv()

# Variables de Azure OpenAI
API_KEY = os.getenv('AZURE_OPENAI_API_KEY')
ENDPOINT = os.getenv('AZURE_OPENAI_ENDPOINT')
DEPLOYMENT = os.getenv('AZURE_OPENAI_DEPLOYMENT')
API_VERSION = os.getenv('AZURE_OPENAI_API_VERSION', '2024-02-15-preview')

# Verificar si Azure OpenAI está configurado
AZURE_OPENAI_CONFIGURED = all([API_KEY, ENDPOINT, DEPLOYMENT])

if AZURE_OPENAI_CONFIGURED:
    try:
        from openai import AzureOpenAI
        print("✅ Azure OpenAI configurado correctamente")
    except ImportError:
        print("❌ Error: No se pudo importar Azure OpenAI")
        AZURE_OPENAI_CONFIGURED = False
else:
    print("⚠️ Azure OpenAI no configurado - usando modo de prueba")
    print("Para configurar Azure OpenAI:")
    print("1. Ve a https://portal.azure.com")
    print("2. Crea un recurso 'Azure OpenAI'")
    print("3. Copia la API Key y Endpoint")
    print("4. Crea un deployment con un modelo (gpt-35-turbo, gpt-4, etc.)")
    print("5. Configura las variables en el archivo .env")

def generar_informe_prueba(perfil: str) -> str:
    """
    Genera un informe de prueba cuando Azure OpenAI no está configurado
    """
    return f"""
# 📋 Informe de Empleabilidad - MODO PRUEBA

## 👤 Resumen del Candidato

Este es un informe de **prueba** generado porque Azure OpenAI no está configurado.

### 📊 Datos Procesados

Se han recibido los siguientes datos del candidato:
- Perfil procesado correctamente
- Datos de habilidades soft evaluadas
- Información del CV analizada
- Preferencias laborales registradas

### 🔧 Configuración Requerida

Para generar informes reales con IA, necesitas configurar Azure OpenAI:

1. **Crear recurso Azure OpenAI** en el portal de Azure
2. **Configurar API Key** y Endpoint
3. **Crear deployment** con un modelo de IA
4. **Actualizar variables de entorno** en el backend

### 📈 Estado Actual

- ✅ **Backend funcionando** correctamente
- ✅ **API endpoints** operativos
- ✅ **CORS configurado** para el frontend
- ⚠️ **Azure OpenAI** pendiente de configuración

### 🎯 Próximos Pasos

1. Configurar Azure OpenAI siguiendo las instrucciones
2. Reiniciar el backend
3. Generar informes reales con IA

---

*Informe generado el {datetime.now().strftime('%d/%m/%Y a las %H:%M')}*
"""

def generar_informe(perfil: str) -> str:
    """
    Genera un informe de empleabilidad usando Azure OpenAI o modo de prueba
    """
    
    if not AZURE_OPENAI_CONFIGURED:
        logger.warning("⚠️ Azure OpenAI no configurado - usando modo de prueba")
        return generar_informe_prueba(perfil)
    
    try:
        # Verificar que las variables no sean None
        if not all([API_KEY, ENDPOINT, DEPLOYMENT]):
            raise ValueError("Variables de Azure OpenAI no configuradas")
        
        # Configurar cliente Azure OpenAI con type assertions
        assert API_KEY is not None
        assert ENDPOINT is not None
        assert DEPLOYMENT is not None
        
        client = AzureOpenAI(
            api_key=API_KEY,
            api_version=API_VERSION,
            azure_endpoint=ENDPOINT,
            timeout=300.0
        )
        
        # Cargar feedback previo
        feedback_previo = cargar_feedback_previo()
        
        # Prompt para Azure OpenAI
        prompt = f"""
Eres un orientador laboral sénior experto en neuroinclusión laboral. Genera un informe de empleabilidad personalizado para personas neurodivergentes.

{feedback_previo}

**DATOS DEL CANDIDATO:**
{perfil}

**FORMATO DE SALIDA:**
- Usa Markdown con encabezados (##, ###)
- Párrafos cortos (máximo 3-4 frases)
- Listas numeradas con formato "1. Título del elemento"
- Lenguaje claro y directo
- Tono positivo y motivador
- Adaptado para neuroinclusión laboral
"""
        
        # Llamar a Azure OpenAI
        response = client.chat.completions.create(
            model=DEPLOYMENT,
            messages=[
                {"role": "system", "content": "Eres un orientador laboral experto en neuroinclusión."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        
        content = response.choices[0].message.content
        return content if content else generar_informe_prueba(perfil)
        
    except Exception as e:
        logger.error(f"❌ Error generando informe con Azure OpenAI: {str(e)}")
        logger.info("🔄 Usando modo de prueba como fallback")
        return generar_informe_prueba(perfil)

def cargar_feedback_previo():
    """
    Carga el feedback previo de los usuarios
    """
    feedback_file = "feedback_ia.json"
    if not os.path.exists(feedback_file):
        return ""
    
    try:
        with open(feedback_file, 'r', encoding='utf-8') as f:
            feedbacks = json.load(f)
        
        if not feedbacks:
            return ""
        
        feedbacks_utiles = [f for f in feedbacks if f.get('rating') == 'Útil']
        
        if not feedbacks_utiles:
            return ""
        
        feedbacks_recientes = feedbacks_utiles[-5:]
        
        feedback_text = "\n\nFEEDBACK PREVIO DE USUARIOS:\n"
        for i, feedback in enumerate(feedbacks_recientes, 1):
            feedback_text += f"\n{i}. {feedback.get('comment', 'Sin comentarios')}"
        
        return feedback_text
        
    except Exception as e:
        logger.warning(f"⚠️ Error cargando feedback previo: {str(e)}")
        return ""
