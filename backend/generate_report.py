# backend/generate_report.py

import os
from openai import AzureOpenAI
from dotenv import load_dotenv
import time

# ─── Cargamos variables de entorno ───
load_dotenv()  # Busca un archivo .env en esta carpeta

API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT")
API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")

if not all([API_KEY, ENDPOINT, DEPLOYMENT, API_VERSION]):
    raise RuntimeError("Faltan variables de entorno de Azure OpenAI")

# Cliente de Azure OpenAI
if not all([API_KEY, ENDPOINT, DEPLOYMENT, API_VERSION]):
    raise RuntimeError("Faltan variables de entorno de Azure OpenAI")

# Verificar que las variables no sean None y hacer type assertion
if not all([API_KEY, ENDPOINT, DEPLOYMENT, API_VERSION]):
    raise RuntimeError("Variables de entorno de Azure OpenAI no pueden ser None")

# Type assertions para asegurar que las variables no sean None
assert API_KEY is not None
assert ENDPOINT is not None
assert DEPLOYMENT is not None
assert API_VERSION is not None

client = AzureOpenAI(
    api_key=API_KEY,
    api_version=API_VERSION,
    azure_endpoint=ENDPOINT,
    timeout=300.0  # 5 minutos de timeout para evitar cancelaciones
)

def generar_informe(perfil: str) -> str:
    """
    Envía el prompt a Azure OpenAI y devuelve el texto completo del informe.
    `perfil` debe contener todo: datos del formulario, scores de softskills y texto del CV.
    """

    prompt = f"""
Eres un orientador laboral senior con estudios en psicología y experto en neuroinclusión laboral. Tu misión es generar un informe de empleabilidad personalizado, preciso, riguroso y profesional para personas neurodivergentes (autismo, TDAH, Dislexia, Tourette, etc.) y/o con discapacidad intelectual. 

En todas las secciones del informe, aplica tu conocimiento en neuroinclusión laboral para adaptar el lenguaje, las recomendaciones y los ejemplos, haciéndolos comprensibles, relevantes y motivadores para este colectivo. El informe debe estar escrito en español de España, utilizando frases cortas y de fácil lectura, con un lenguaje profesional pero cercano. Evita metáforas complejas, sarcasmo o ambigüedades. Utiliza un lenguaje directo, positivo y, cuando sea apropiado, proporciona instrucciones paso a paso. Utiliza únicamente los datos proporcionados, evitando información de relleno.

IMPORTANTE: Genera un informe EXTENSO y COMPLETO. Cada sección debe tener al menos 3-4 párrafos detallados. NO seas escueto ni superficial.

OBLIGATORIO: Debes incluir SIEMPRE los datos reales del CV que aparecen en la sección 'ANÁLISIS DETALLADO DEL CV'. Cita específicamente la experiencia laboral, formación académica, habilidades técnicas y cualquier otra información relevante del CV en las secciones correspondientes.

---

DATOS DEL CANDIDATO A ANALIZAR:
{perfil}

---

El informe debe seguir la siguiente estructura y contenido:

## 1. Resumen del perfil
- Crear un resumen conciso y estructurado del candidato en formato de puntos, incluyendo:
  - **Datos personales básicos**: Nombre y características principales
  - **Resumen del CV**: CITA ESPECÍFICAMENTE la experiencia laboral, formación académica, habilidades técnicas detectadas del CV (incluye fechas, empresas, puestos, estudios, etc. que aparezcan en la sección 'ANÁLISIS DETALLADO DEL CV')
  - **Preferencias laborales**: Áreas de interés, modo de trabajo preferido, disponibilidad, necesidades específicas (basándose en la sección 'PREFERENCIAS LABORALES')
  - **Perfil de habilidades**: Resumen de las soft skills más destacadas con sus niveles (basándose en la sección 'HABILIDADES SOFT EVALUADAS')
- Utilizar un formato claro y fácil de leer, con viñetas y subsecciones bien organizadas
- Mantener un tono profesional pero accesible

## 2. Fortalezas clave
- Listar las habilidades blandas identificadas con nivel "alto" en la sección de 'HABILIDADES SOFT EVALUADAS'. Al describir cada fortaleza, considera el nivel de 'Confianza' del candidato para reforzar su autoconfianza y validar sus percepciones.
- Para cada fortaleza, proporcionar un ejemplo práctico de cómo el candidato puede usarla en un entorno laboral.
- INCLUYE OBLIGATORIAMENTE las fortalezas identificadas en el análisis del CV (sección 'ANÁLISIS DETALLADO DEL CV'). Cita específicamente las habilidades técnicas, experiencia relevante y logros mencionados en el CV.

## 3. Áreas a mejorar
- Identificar un máximo de 4 habilidades blandas con nivel "bajo" o "medio" de la sección de 'HABILIDADES SOFT EVALUADAS'.
- Para cada área, ofrecer consejos prácticos y accesibles (ej. "pasos a seguir" o sugerencias de recursos como "vídeos recomendados"). Al formular estos consejos, ten en cuenta el nivel de 'Confianza' del candidato, ofreciendo estrategias que ayuden a construirla y a superar posibles inseguridades.
- INCLUYE OBLIGATORIAMENTE las áreas de mejora identificadas en el análisis del CV. Cita específicamente las debilidades o aspectos a mejorar mencionados en el CV.

## 4. Sugerencias laborales
- Basándose en las preferencias laborales del candidato (sección 'PREFERENCIAS LABORALES'), el análisis detallado de los resultados de los minijuegos (sección 'LOGS DE JUEGOS') y el análisis del CV, sugerir:
  - Entornos de trabajo ideales (ej. colaborativo, autónomo, estructurado, flexible), considerando las tendencias observadas en los minijuegos (ej. preferencia por tareas repetitivas, resolución de problemas bajo presión, interacción social).
  - Tipos de tareas recomendadas que se alineen con sus fortalezas y preferencias, respaldadas por el rendimiento y las preferencias mostradas en los minijuegos y su experiencia profesional, mostrada en el CV.
  - Consejos de búsqueda de empleo adaptados a su estilo y necesidades (ej. plataformas específicas, networking, preparación de entrevistas), teniendo en cuenta cómo el candidato gestiona la información y el estrés según los logs de los juegos.
  - Adaptaciones específicas que puede solicitar en el entorno laboral basadas en sus necesidades y preferencias.
- REFERENCIA ESPECÍFICA a la experiencia laboral del CV para respaldar las sugerencias.

## 5. Evaluación del CV
- Realizar un análisis visual del CV (sección 'ANÁLISIS DETALLADO DEL CV') considerando:
  - Estructura y coherencia.
  - Áreas de mejora. Proporciona ejemplos concretos de cómo adaptar el CV para destacar habilidades relevantes y cómo presentar la información de manera clara y concisa.
- Utilizar iconos para representar:
  - Formato.
  - Claridad.
  - Información clave.
  - Ortografía.
- Proporcionar recomendaciones personalizadas para optimizar el CV.
- Incluir sugerencias específicas para adaptar el CV a diferentes tipos de empresas y puestos.
- CITA ESPECÍFICAMENTE elementos del CV analizado para respaldar tus recomendaciones.

## 6. Próximos pasos
- Sugerir formación relevante basada en las áreas a mejorar y las preferencias laborales. Prioriza formaciones accesibles y adaptadas a diferentes estilos de aprendizaje.
- Recomendar portales de empleo específicos para personas con o sin discapacidad, o aquellos que se adapten a sus preferencias. Menciona plataformas que prioricen la inclusión o que tengan filtros específicos para adaptaciones y necesidades especiales.
- Incluir una frase de motivación final.
- Proporcionar un plan de acción concreto con fechas y objetivos específicos.
- REFERENCIA a la experiencia y formación del CV para personalizar las recomendaciones.

## 7. Recursos y apoyo adicional
- Listar organizaciones y asociaciones que ofrecen apoyo específico para personas neurodivergentes en el ámbito laboral.
- Recomendar herramientas y tecnologías de apoyo que puedan facilitar el desempeño laboral.
- Incluir contactos de orientadores laborales especializados en neuroinclusión.

---

CRITERIOS DE CALIDAD OBLIGATORIOS:
- Lenguaje profesional pero accesible, sin jerga técnica compleja
- Análisis basado en evidencia y experiencia en neuroinclusión
- Recomendaciones prácticas y realizables, con ejemplos concretos
- Enfoque positivo y empoderador, destacando fortalezas
- Consideración integral de factores neuroinclusivos
- Propuestas específicas y contextualizadas
- MÍNIMO 2500 palabras de contenido sustancial
- Cada sección debe tener al menos 3-4 párrafos detallados
- Incluir ejemplos concretos y casos de uso específicos
- Proporcionar recursos específicos, accionables y verificables
- Utilizar un tono motivador y constructivo
- Evitar generalizaciones y estereotipos
- Incluir perspectivas de desarrollo a corto, medio y largo plazo
- OBLIGATORIO: Citar y referenciar específicamente los datos del CV en las secciones correspondientes
"""

    # Llamada a la API con timeout extendido
    try:
        respuesta = client.chat.completions.create(
            model=DEPLOYMENT,  # type: ignore
            messages=[
                {"role": "system", "content": "Eres un psicólogo laboral experto en neuroinclusión, con más de 15 años de experiencia en orientación profesional para personas neurodivergentes. Tienes formación en psicología clínica, neuropsicología y empleabilidad. Tu enfoque es científico, empático y basado en evidencia. Siempre consideras las fortalezas únicas de cada persona y propones adaptaciones prácticas para maximizar su potencial laboral. IMPORTANTE: Genera informes EXTENSOS y DETALLADOS, no seas escueto."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=8000,
            temperature=0.7
        )
        
        return respuesta.choices[0].message.content or ""
        
    except Exception as e:
        # Si hay un timeout o error, intentar con un prompt más corto
        print(f"⚠️ Error en la primera llamada a la API: {str(e)}")
        print("🔄 Intentando con prompt más corto...")
        
        # Prompt más corto como fallback
        prompt_corto = f"""
Genera un informe de empleabilidad profesional para el siguiente candidato:

{perfil}

El informe debe incluir:
1. Resumen del perfil
2. Fortalezas clave
3. Áreas a mejorar
4. Sugerencias laborales
5. Próximos pasos

Genera un informe completo pero más conciso.
"""
        
        respuesta = client.chat.completions.create(
            model=DEPLOYMENT,  # type: ignore
            messages=[
                {"role": "system", "content": "Eres un psicólogo laboral experto en neuroinclusión."},
                {"role": "user", "content": prompt_corto}
            ],
            max_tokens=4000,
            temperature=0.7
        )
        
        return respuesta.choices[0].message.content or ""
