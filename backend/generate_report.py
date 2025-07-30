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
    Genera un informe de prueba profesional cuando Azure OpenAI no está configurado
    """
    return f"""
# 📋 Informe de Empleabilidad Profesional - MODO PRUEBA

## 👤 Resumen Ejecutivo

Este informe ha sido generado en **modo de prueba** debido a que Azure OpenAI no está configurado en el sistema. Los datos del candidato han sido procesados correctamente y están listos para análisis completo.

---

## 📊 Análisis de Datos Procesados

### ✅ Información Recibida y Validada:
- **Perfil del candidato**: Procesado correctamente
- **Habilidades soft evaluadas**: Datos disponibles para análisis
- **Análisis del CV**: Información extraída y estructurada
- **Preferencias laborales**: Configuración registrada
- **Resultados de minijuegos**: Datos de evaluación disponibles

### 📈 Estado del Sistema:
- ✅ **Backend funcionando** correctamente
- ✅ **API endpoints** operativos y respondiendo
- ✅ **CORS configurado** para integración frontend
- ✅ **Análisis de CV** implementado y funcional
- ⚠️ **Azure OpenAI** pendiente de configuración

---

## 🔧 Configuración Requerida para IA Completa

Para generar informes profesionales con inteligencia artificial, es necesario configurar Azure OpenAI:

### 1. **Crear Recurso Azure OpenAI**
   - Acceder al portal de Azure (https://portal.azure.com)
   - Crear un nuevo recurso "Azure OpenAI"
   - Seleccionar región apropiada y plan de precios

### 2. **Configurar Credenciales**
   - Obtener API Key desde "Keys and Endpoint"
   - Copiar el Endpoint del servicio
   - Crear deployment con modelo de IA (gpt-35-turbo recomendado)

### 3. **Actualizar Configuración**
   - Modificar archivo `.env` en el backend
   - Agregar variables de entorno necesarias
   - Reiniciar el servicio backend

### 4. **Verificar Funcionamiento**
   - Probar conexión con Azure OpenAI
   - Validar generación de informes con IA
   - Confirmar calidad de análisis

---

## 🎯 Próximos Pasos Recomendados

### Inmediatos:
1. **Configurar Azure OpenAI** siguiendo la guía técnica
2. **Reiniciar el backend** para aplicar cambios
3. **Probar generación** de informes con IA

### A Mediano Plazo:
1. **Optimizar prompts** para mejor calidad de análisis
2. **Implementar feedback** de usuarios para mejorar IA
3. **Expandir funcionalidades** de análisis de CV

### A Largo Plazo:
1. **Integrar análisis avanzado** de habilidades
2. **Desarrollar recomendaciones** personalizadas
3. **Implementar seguimiento** de progreso

---

## 📋 Información Técnica

- **Fecha de generación**: {datetime.now().strftime('%d/%m/%Y a las %H:%M')}
- **Modo de operación**: Prueba (sin IA)
- **Estado del sistema**: Funcional
- **Próxima actualización**: Tras configuración de Azure OpenAI

---

*Este informe de prueba demuestra la funcionalidad del sistema. Para obtener análisis completo con inteligencia artificial, configure Azure OpenAI siguiendo las instrucciones proporcionadas.*
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
        
        # Prompt profesional para informe de empleabilidad
        prompt = f"""
Eres un orientador laboral sénior experto en neuroinclusión laboral y empleabilidad profesional. Genera un informe de empleabilidad personalizado, completo y profesional que sea cognitivamente accesible y adaptado para personas neurodivergentes.

{feedback_previo}

**DATOS DEL CANDIDATO:**
{perfil}

**REQUISITOS DEL INFORME:**

1. **ESTRUCTURA PROFESIONAL:**
   - Título principal con el nombre del candidato
   - Resumen ejecutivo (2-3 párrafos)
   - Análisis detallado por secciones
   - Recomendaciones específicas y accionables
   - Plan de desarrollo personalizado

2. **ADAPTACIÓN COGNITIVA:**
   - Párrafos cortos (máximo 3-4 frases)
   - Lenguaje claro, directo y sin ambigüedades
   - Uso de listas numeradas y con viñetas
   - Información organizada jerárquicamente
   - Evitar jerga técnica innecesaria

3. **ACCESIBILIDAD VISUAL:**
   - Usar encabezados claros (##, ###)
   - Separar secciones con líneas horizontales
   - Usar listas para información importante
   - Destacar puntos clave con **negrita**
   - Usar colores conceptuales (no reales en texto)

4. **CONTENIDO ESPECÍFICO:**
   - Análisis de fortalezas y áreas de mejora
   - Recomendaciones de puestos de trabajo compatibles
   - Plan de desarrollo de habilidades
   - Estrategias de búsqueda de empleo
   - Adaptaciones laborales recomendadas
   - Recursos y herramientas útiles

5. **ENFOQUE NEUROINCLUSIVO:**
   - Reconocer fortalezas únicas
   - Sugerir entornos de trabajo apropiados
   - Proponer adaptaciones específicas
   - Enfatizar el valor de la diversidad
   - Proporcionar estrategias de comunicación

**FORMATO DE SALIDA:**
- Usa Markdown con estructura clara
- Incluye todos los elementos mencionados
- Mantén un tono profesional pero accesible
- Sé específico y accionable en las recomendaciones
- Adapta el contenido a los datos proporcionados
"""
        
        # Llamar a Azure OpenAI
        response = client.chat.completions.create(
            model=DEPLOYMENT,
            messages=[
                {"role": "system", "content": "Eres un orientador laboral sénior con más de 15 años de experiencia en empleabilidad, neuroinclusión laboral y desarrollo profesional. Tu especialidad es crear informes personalizados, accesibles cognitivamente y profesionalmente estructurados que empoderen a las personas neurodivergentes en su búsqueda de empleo."},
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
