# backend/generate_report.py

"""
Módulo de generación de informes de empleabilidad

IMPORTANTE: Este módulo NO contiene prompts hardcodeados. Todos los prompts están centralizados
en prompt_config.py para evitar duplicación y facilitar el mantenimiento.

- generar_informe_prueba(): Genera informe de prueba usando el prompt centralizado
- generar_informe(): Genera informe completo usando Azure OpenAI con prompt centralizado
- cargar_feedback_previo(): Carga feedback previo de usuarios

Todos los prompts se obtienen de PromptConfig.get_employability_report_prompt()
"""

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

def generar_informe_prueba(
    candidate_data: dict,
    soft_skills_data: list,
    cv_data: dict,
    job_preferences_data: dict,
    employability_score: int,
    level: str,
    completed_games: list,
    languages_data: list
) -> str:
    """
    Genera un informe de prueba profesional cuando Azure OpenAI no está configurado
    IMPORTANTE: Los minijuegos y CV son obligatorios para todos los candidatos
    """
    
    # Importar PromptConfig para usar el prompt centralizado
    try:
        from .prompt_config import PromptConfig
    except ImportError:
        from prompt_config import PromptConfig
    
    # Usar el prompt centralizado para mantener consistencia
    prompt = PromptConfig.get_employability_report_prompt(
        candidate_data=candidate_data,
        soft_skills_data=soft_skills_data,
        cv_data=cv_data,
        job_preferences_data=job_preferences_data,
        employability_score=employability_score,
        level=level,
        completed_games=completed_games,
        languages_data=languages_data
    )
    
    # Generar informe de prueba basado en el prompt centralizado
    # pero adaptado para modo de prueba (sin llamar a Azure OpenAI)
    return f"""
# 📋 Informe de Empleabilidad Profesional - MODO PRUEBA

**NOTA IMPORTANTE:** Este es un informe de prueba generado porque Azure OpenAI no está configurado. Para obtener un análisis completo y personalizado con inteligencia artificial, sigue las instrucciones de configuración.

## 1. DATOS PERSONALES BÁSICOS
- **Nombre**: {candidate_data.get('fullName', 'No consta')}
- **Email**: {candidate_data.get('email', 'No consta')}
- **Teléfono**: {candidate_data.get('phone', 'No consta')}
- **Ubicación**: {candidate_data.get('location', 'No consta')}
- **Certificado de discapacidad**: {'Sí' if candidate_data.get('hasDisabilityCertificate') else 'No' if candidate_data.get('hasDisabilityCertificate') is False else 'No consta'}

## 2. RESUMEN DEL PERFIL
Perfil profesional con puntuación de empleabilidad de {employability_score}/100, {level}. Los minijuegos han sido completados exitosamente y el CV ha sido analizado por las herramientas de IA.

## 3. RESUMEN DEL CV
- **Experiencia laboral**: {len(cv_data.get('sections', {}).get('experience', []))} posiciones detectadas
- **Formación académica**: {len(cv_data.get('sections', {}).get('education', []))} elementos educativos
- **Idiomas**: {len(cv_data.get('sections', {}).get('languages', []))} idiomas identificados
- **Software/Herramientas**: {len(cv_data.get('sections', {}).get('software', []))} herramientas detectadas

## 4. FORTALEZAS (CRUZANDO MINIJUEGOS Y CV)
- **Habilidades soft evaluadas**: {len(soft_skills_data)} competencias evaluadas en minijuegos
- **Competencias identificadas**: Basadas en CV y evaluación de minijuegos
- **Puntos fuertes**: Análisis disponible de soft skills y experiencia

## 5. ÁREAS DE MEJORA Y CONSEJOS (PRIORIZADAS Y ACCIONABLES)
- **Oportunidades de desarrollo**: Basadas en resultados de minijuegos y análisis de CV
- **Consejos específicos**: Disponibles tras configuración completa de IA
- **Enfoque constructivo**: Implementado en el sistema

## 6. ANÁLISIS DEL CV CON PUNTUACIÓN 1–5 POR APARTADO
**Estructura:** ★★★☆☆ (Regular) - Análisis básico disponible
**Claridad:** ★★★☆☆ (Regular) - Información estructurada
**Coherencia:** ★★★☆☆ (Regular) - Datos organizados
**Información clave:** ★★★☆☆ (Regular) - Contenido procesado
**Ortografía:** ★★★☆☆ (Regular) - Revisión básica

*Consejos detallados disponibles tras configuración de IA completa.*

## 7. ENTORNOS DE TRABAJO IDEALES
- **Modalidad preferida**: {', '.join(job_preferences_data.get('work_modes', ['No especificado']))}
- **Disponibilidad**: {job_preferences_data.get('availability', 'No especificado')}
- **Relocalización**: {'Sí' if job_preferences_data.get('relocation') else 'No' if job_preferences_data.get('relocation') is False else 'No consta'}

## 8. ROLES PROFESIONALES SUGERIDOS (ALINEADOS CON EXPERIENCIA Y PREFERENCIAS)
- **Puestos compatibles**: Análisis disponible según CV y preferencias
- **Sectores**: {', '.join(job_preferences_data.get('desired_sectors', ['No especificado']))}
- **Modalidad de trabajo**: {', '.join(job_preferences_data.get('work_modes', ['No especificado']))}

## 9. PLAN DE ACCIÓN A CORTO, MEDIO Y LARGO PLAZO
**Corto plazo (0-30 días):**
- Configurar Azure OpenAI para análisis completo
- Probar funcionalidades de IA
- Validar calidad de informes

**Medio plazo (1-3 meses):**
- Optimizar prompts de IA
- Implementar feedback de usuarios
- Mejorar análisis de CV

**Largo plazo (3-6+ meses):**
- Expandir funcionalidades
- Integrar análisis avanzado
- Desarrollar recomendaciones personalizadas

## 10. CONSEJOS DE BÚSQUEDA DE EMPLEO (CV, NETWORKING, PLATAFORMAS, ENTREVISTAS)
- **Estrategias activas**: Recomendaciones disponibles
- **Plataformas de empleo**: LinkedIn, InfoJobs, Empléate
{'**Plataformas inclusivas**: Inserta Empleo, Plena Inclusión' if candidate_data.get('hasDisabilityCertificate') else ''}

## 11. HERRAMIENTAS ÚTILES Y TECNOLOGÍA
- **Plataformas de formación**: Coursera, edX, Google Digital
- **Herramientas tecnológicas**: Integradas
- **Recursos profesionales**: Accesibles

## 12. JUEGOS COMPLETADOS (Y QUÉ EVIDENCIAN)
{', '.join(completed_games) if completed_games else 'No consta'} - Evaluación de soft skills completada

## 13. FRASE FINAL DE CIERRE MOTIVACIONAL Y PERSONALIZADA
Este informe se ha realizado teniendo en cuenta toda la información que nos has proporcionado y tus preferencias laborales. Aprovecha tus fortalezas y confía en tu potencial. ¡Mucha suerte!

---

**NOTA IMPORTANTE:** Este es un informe de prueba generado porque Azure OpenAI no está configurado. Para obtener un análisis completo y personalizado con inteligencia artificial, sigue las instrucciones de configuración en `azure_openai_setup.md`.

**IMPORTANTE:** Los minijuegos y CV son obligatorios para todos los candidatos y han sido completados exitosamente.

**Fecha de generación:** {datetime.now().strftime('%d/%m/%Y a las %H:%M')}
"""

def generar_informe(
    candidate_data: dict,
    soft_skills_data: list,
    cv_data: dict,
    job_preferences_data: dict,
    employability_score: int,
    level: str,
    completed_games: list,
    languages_data: list
) -> str:
    """
    Genera un informe de empleabilidad usando Azure OpenAI o modo de prueba
    IMPORTANTE: Los minijuegos y CV son obligatorios para todos los candidatos
    """
    
    if not AZURE_OPENAI_CONFIGURED:
        logger.warning("⚠️ Azure OpenAI no configurado - usando modo de prueba")
        return generar_informe_prueba(
            candidate_data, soft_skills_data, cv_data, job_preferences_data,
            employability_score, level, completed_games, languages_data
        )
    
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
        
        # Importar PromptConfig para usar el prompt centralizado
        try:
            from .prompt_config import PromptConfig
        except ImportError:
            from prompt_config import PromptConfig
        
        # Usar prompt centralizado para informe de empleabilidad
        # IMPORTANTE: Los minijuegos y CV son obligatorios para todos los candidatos
        prompt = PromptConfig.get_employability_report_prompt(
            candidate_data=candidate_data,
            soft_skills_data=soft_skills_data,
            cv_data=cv_data,
            job_preferences_data=job_preferences_data,
            employability_score=employability_score,
            level=level,
            completed_games=completed_games,
            languages_data=languages_data
        )
        
        # Llamar a Azure OpenAI
        # Sanitizar el esquema antes de enviarlo
        report_schema = PromptConfig.get_report_schema()
        
        def _close_schema(obj: dict) -> dict:
            """
            Recorre recursivamente un JSON Schema y añade `"additionalProperties": false`
            a todos los nodos con type:"object" donde no esté definido.
            """
            if not isinstance(obj, dict):
                return obj

            t = obj.get("type")

            # Si es objeto, ciérralo
            if t == "object":
                obj.setdefault("additionalProperties", False)
                props = obj.get("properties")
                if isinstance(props, dict):
                    for _, sub in props.items():
                        _close_schema(sub)

            # Si es array, baja a items
            if t == "array" and "items" in obj:
                _close_schema(obj["items"])

            # Combinadores
            for k in ("oneOf", "anyOf", "allOf"):
                if k in obj and isinstance(obj[k], list):
                    for sub in obj[k]:
                        _close_schema(sub)

            # También recorre cualquier sub-dict residual por seguridad
            for k, v in list(obj.items()):
                if isinstance(v, dict) and k not in ("properties", "items"):
                    _close_schema(v)
                elif isinstance(v, list) and k not in ("oneOf", "anyOf", "allOf"):
                    for it in v:
                        if isinstance(it, dict):
                            _close_schema(it)

            return obj
        
        report_schema = _close_schema(report_schema)
        
        response = client.chat.completions.create(
            model=DEPLOYMENT,
            messages=[
                {"role": "system", "content": PromptConfig.get_system_prompt()},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=3000,
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "EmployabilityReport",
                    "schema": report_schema,
                    "strict": True
                }
            }
        )
        
        content = response.choices[0].message.content
        
        # Si la respuesta es JSON, convertirla a formato de informe legible
        if content and content.strip().startswith('{'):
            try:
                # Parsear la respuesta JSON
                json_response = json.loads(content)
                
                # Convertir el JSON estructurado a formato de informe markdown
                return PromptConfig.convert_json_to_markdown_report(json_response)
                
            except json.JSONDecodeError as e:
                logger.warning(f"⚠️ Error parseando respuesta JSON: {str(e)}")
                # Si falla el parsing, usar la respuesta raw
                return content if content else generar_informe_prueba(
                    candidate_data, soft_skills_data, cv_data, job_preferences_data,
                    employability_score, level, completed_games, languages_data
                )
        else:
            # Si no es JSON, usar la respuesta directamente
            return content if content else generar_informe_prueba(
                candidate_data, soft_skills_data, cv_data, job_preferences_data,
                employability_score, level, completed_games, languages_data
            )
        
    except Exception as e:
        logger.error(f"❌ Error generando informe con Azure OpenAI: {str(e)}")
        logger.info("🔄 Usando modo de prueba como fallback")
        return generar_informe_prueba(
            candidate_data, soft_skills_data, cv_data, job_preferences_data,
            employability_score, level, completed_games, languages_data
        )

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
