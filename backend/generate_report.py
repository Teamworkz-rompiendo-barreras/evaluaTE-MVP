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
API_VERSION = os.getenv('AZURE_OPENAI_API_VERSION', '2024-11-20')

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

## 1. DATOS PERSONALES BÁSICOS
- **Nombre**: [Datos del candidato procesados correctamente]
- **Información de contacto**: Disponible en el sistema
- **Ubicación**: Registrada en preferencias laborales

## 2. RESUMEN DEL CV
- **Experiencia laboral**: Información extraída y estructurada
- **Formación académica**: Datos disponibles para análisis
- **Habilidades principales**: Identificadas en el CV
- **Logros relevantes**: Procesados correctamente

## 3. PREFERENCIAS LABORALES
- **Áreas de interés**: Configuradas en el sistema
- **Necesidades específicas**: Registradas correctamente
- **Modalidad de trabajo**: Preferencias establecidas
- **Disponibilidad**: Información disponible

## 4. FORTALEZAS
- **Habilidades soft evaluadas**: Datos de minijuegos disponibles
- **Competencias identificadas**: Basadas en CV y evaluación
- **Puntos fuertes**: Análisis disponible
- **Perfil profesional**: Información estructurada

## 5. ÁREAS DE MEJORA Y CONSEJOS
- **Oportunidades de desarrollo**: Basadas en resultados de minijuegos
- **Consejos específicos**: Disponibles tras configuración de IA
- **Enfoque constructivo**: Implementado en el sistema
- **Plan de mejora**: Personalizado según perfil

## 6. ROLES PROFESIONALES SUGERIDOS
- **Puestos compatibles**: Análisis disponible
- **Rangos salariales**: Información de mercado
- **Requisitos típicos**: Datos actualizados
- **Oportunidades**: Identificadas según perfil

## 7. CONSEJOS PARA LA BÚSQUEDA DE EMPLEO
- **Estrategias activas**: Recomendaciones disponibles
- **Adaptación de CV**: Consejos específicos
- **Plataformas de empleo**: Lista actualizada
- **Networking**: Estrategias efectivas

## 8. ANÁLISIS DE CV
**Formato:** ★★★☆☆ (Regular) - Análisis básico disponible
**Claridad:** ★★★☆☆ (Regular) - Información estructurada
**Coherencia:** ★★★☆☆ (Regular) - Datos organizados
**Información clave:** ★★★☆☆ (Regular) - Contenido procesado
**Ortografía:** ★★★☆☆ (Regular) - Revisión básica

*Consejos detallados disponibles tras configuración de IA completa.*

## 9. PLAN DE ACCIÓN
**Corto plazo (1-3 meses):**
- Configurar Azure OpenAI para análisis completo
- Probar funcionalidades de IA
- Validar calidad de informes

**Medio plazo (3-6 meses):**
- Optimizar prompts de IA
- Implementar feedback de usuarios
- Mejorar análisis de CV

**Largo plazo (6-12 meses):**
- Expandir funcionalidades
- Integrar análisis avanzado
- Desarrollar recomendaciones personalizadas

## 10. HERRAMIENTAS ÚTILES Y TECNOLOGÍA
- **Plataformas de formación**: Disponibles en el sistema
- **Herramientas tecnológicas**: Integradas
- **Recursos profesionales**: Accesibles
- **Aplicaciones útiles**: Recomendadas

## 11. MENSAJE FINAL
Este informe se ha realizado teniendo en cuenta toda la información que nos has facilitado y tus preferencias laborales. Aprovecha tus fortalezas y confía en tu potencial. ¡Mucha suerte!

---

**NOTA IMPORTANTE:** Este es un informe de prueba generado porque Azure OpenAI no está configurado. Para obtener un análisis completo y personalizado con inteligencia artificial, sigue las instrucciones de configuración en `azure_openai_setup.md`.

**Fecha de generación:** {datetime.now().strftime('%d/%m/%Y a las %H:%M')}
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
        
        # Prompt profesional para informe de empleabilidad con formato específico
        prompt = f"""
Eres un orientador laboral sénior experto en empleabilidad profesional. Genera un informe de empleabilidad personalizado, completo y profesional con el formato exacto que se especifica.

{feedback_previo}

**DATOS DEL CANDIDATO:**
{perfil}

**FORMATO OBLIGATORIO DEL INFORME:**

El informe debe seguir EXACTAMENTE esta estructura con estos 11 apartados:

## 1. DATOS PERSONALES BÁSICOS
- Nombre completo del candidato
- Información de contacto relevante
- Ubicación geográfica

## 2. RESUMEN DEL CV
- Resumen ejecutivo de la experiencia laboral
- Formación académica destacada
- Habilidades principales identificadas
- Logros más relevantes

## 3. PREFERENCIAS LABORALES
- Áreas de interés profesional
- Necesidades específicas del candidato
- Modalidad de trabajo preferida
- Disponibilidad y flexibilidad

## 4. FORTALEZAS
- Basadas en los resultados de los minijuegos
- Habilidades identificadas en el CV
- Competencias destacadas
- Puntos fuertes del perfil profesional

## 5. ÁREAS DE MEJORA Y CONSEJOS
- Basadas en los resultados de los minijuegos
- Oportunidades de desarrollo
- Consejos específicos y accionables
- Enfoque constructivo y motivador

## 6. ROLES PROFESIONALES SUGERIDOS
- Puestos de trabajo compatibles
- Considerando preferencias laborales y CV
- Rangos salariales aproximados
- Requisitos típicos para cada rol

## 7. CONSEJOS PARA LA BÚSQUEDA DE EMPLEO
- Estrategias de búsqueda activa
- Adaptación del CV para diferentes puestos
- Plataformas de búsqueda de empleo generales
- Plataformas de empleo inclusivo (SOLO si el candidato tiene certificado de discapacidad)
- Networking y contactos profesionales

## 8. ANÁLISIS DE CV
Evaluar cada aspecto con estrellas amarillas (★★★★★) y calificación:

**Formato:** ★★★★★ (Excelente) / ★★★★☆ (Buena) / ★★★☆☆ (Regular) / ★★☆☆☆ (Necesita mejora)
**Claridad:** ★★★★★ (Excelente) / ★★★★☆ (Buena) / ★★★☆☆ (Regular) / ★★☆☆☆ (Necesita mejora)
**Coherencia:** ★★★★★ (Excelente) / ★★★★☆ (Buena) / ★★★☆☆ (Regular) / ★★☆☆☆ (Necesita mejora)
**Información clave:** ★★★★★ (Excelente) / ★★★★☆ (Buena) / ★★★☆☆ (Regular) / ★★☆☆☆ (Necesita mejora)
**Ortografía:** ★★★★★ (Excelente) / ★★★★☆ (Buena) / ★★★☆☆ (Regular) / ★★☆☆☆ (Necesita mejora)

Consejos específicos para mejorar cada aspecto.

## 9. PLAN DE ACCIÓN
**Corto plazo (1-3 meses):**
- Acciones inmediatas y específicas
- Objetivos alcanzables

**Medio plazo (3-6 meses):**
- Desarrollo de habilidades
- Mejoras en el CV

**Largo plazo (6-12 meses):**
- Objetivos profesionales
- Plan de carrera

## 10. HERRAMIENTAS ÚTILES Y TECNOLOGÍA
- Plataformas de formación recomendadas
- Herramientas tecnológicas útiles
- Recursos para el desarrollo profesional
- Aplicaciones y software relevante

## 11. MENSAJE FINAL
"Este informe se ha realizado teniendo en cuenta toda la información que nos has facilitado y tus preferencias laborales. Aprovecha tus fortalezas y confía en tu potencial. ¡Mucha suerte!"

**REQUISITOS ESPECÍFICOS:**
- Tono optimista pero realista
- Evitar ser fantasioso con las expectativas
- NO mencionar que se trata de un perfil neurodivergente
- Lenguaje profesional y accesible
- Recomendaciones específicas y accionables
- Usar estrellas amarillas (★★★★★) para el análisis de CV
- Incluir plataformas de empleo inclusivo SOLO si hay certificado de discapacidad
- Mantener la estructura exacta de 11 apartados
"""
        
        # Llamar a Azure OpenAI
        response = client.chat.completions.create(
            model=DEPLOYMENT,
            messages=[
                {"role": "system", "content": "Eres un orientador laboral sénior con más de 15 años de experiencia en empleabilidad y desarrollo profesional. Tu especialidad es crear informes personalizados y profesionalmente estructurados que sigan exactamente el formato especificado, con análisis detallado de CV usando estrellas, recomendaciones realistas y planes de acción específicos."},
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
