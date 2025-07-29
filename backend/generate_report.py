# backend/generate_report.py

import os
from openai import AzureOpenAI
from dotenv import load_dotenv
import time
import json

# ─── Cargamos variables de entorno ───
load_dotenv()  # Busca un archivo .env en esta carpeta

API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT")
API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")

# Verificar que todas las variables de Azure OpenAI estén configuradas
missing_vars = []
if not API_KEY:
    missing_vars.append("AZURE_OPENAI_API_KEY")
if not ENDPOINT:
    missing_vars.append("AZURE_OPENAI_ENDPOINT")
if not DEPLOYMENT:
    missing_vars.append("AZURE_OPENAI_DEPLOYMENT")
if not API_VERSION:
    missing_vars.append("AZURE_OPENAI_API_VERSION")

if missing_vars:
    error_msg = f"❌ Faltan variables de entorno de Azure OpenAI: {', '.join(missing_vars)}"
    error_msg += "\n\nPara configurar Azure OpenAI:"
    error_msg += "\n1. Ve a https://portal.azure.com"
    error_msg += "\n2. Crea un recurso 'Azure OpenAI'"
    error_msg += "\n3. Copia la API Key y Endpoint"
    error_msg += "\n4. Crea un deployment con un modelo (gpt-35-turbo, gpt-4, etc.)"
    error_msg += "\n5. Configura las variables en el archivo .env"
    raise RuntimeError(error_msg)

# Type assertions para Pyright - después de la verificación sabemos que no son None
assert API_KEY is not None
assert ENDPOINT is not None
assert DEPLOYMENT is not None
assert API_VERSION is not None

# Cliente de Azure OpenAI
try:
    client = AzureOpenAI(
        api_key=API_KEY,
        api_version=API_VERSION,
        azure_endpoint=ENDPOINT,
        timeout=300.0  # 5 minutos de timeout para evitar cancelaciones
    )
    print(f"✅ Cliente Azure OpenAI configurado correctamente")
    print(f"   Endpoint: {ENDPOINT}")
    print(f"   Deployment: {DEPLOYMENT}")
    print(f"   API Version: {API_VERSION}")
except Exception as e:
    error_msg = f"❌ Error configurando cliente Azure OpenAI: {str(e)}"
    error_msg += "\n\nVerifica que:"
    error_msg += "\n1. La API Key sea correcta"
    error_msg += "\n2. El Endpoint sea válido"
    error_msg += "\n3. El deployment exista en tu recurso de Azure OpenAI"
    error_msg += "\n4. Tengas permisos para usar el deployment"
    raise RuntimeError(error_msg)

def cargar_feedback_previo():
    """
    Carga el feedback previo de los usuarios para mejorar los informes futuros.
    """
    feedback_file = "feedback_ia.json"
    if not os.path.exists(feedback_file):
        return ""
    
    try:
        with open(feedback_file, 'r', encoding='utf-8') as f:
            feedbacks = json.load(f)
        
        if not feedbacks:
            return ""
        
        # Filtrar solo feedback útil (rating "Útil")
        feedbacks_utiles = [f for f in feedbacks if f.get('rating') == 'Útil']
        
        if not feedbacks_utiles:
            return ""
        
        # Tomar los últimos 5 feedbacks útiles para no sobrecargar el prompt
        feedbacks_recientes = feedbacks_utiles[-5:]
        
        feedback_text = "\n\nFEEDBACK PREVIO DE USUARIOS (para mejorar el informe):\n"
        for i, feedback in enumerate(feedbacks_recientes, 1):
            feedback_text += f"\n{i}. Comentario: {feedback.get('comment', 'Sin comentarios')}"
            feedback_text += f"\n   Rating: {feedback.get('rating', 'No especificado')}"
            if feedback.get('userData'):
                feedback_text += f"\n   Contexto: Usuario con {len(feedback['userData'].get('minigames', []))} habilidades evaluadas"
        
        return feedback_text
        
    except Exception as e:
        print(f"⚠️ Error cargando feedback previo: {str(e)}")
        return ""

def generar_informe(perfil: str) -> str:
    """
    Envía el prompt a Azure OpenAI y devuelve el texto completo del informe.
    `perfil` debe contener todo: datos del formulario, scores de softskills y análisis detallado del CV.
    """

    # Cargar feedback previo para mejorar el informe
    feedback_previo = cargar_feedback_previo()

    prompt = f"""
Eres un orientador laboral sénior con estudios en psicología y experto en neuroinclusión laboral. Tu misión es generar un informe de empleabilidad personalizado, preciso, riguroso y profesional para personas neurodivergentes (autismo, TDAH, dislexia, Tourette, etc.) y/o con discapacidad intelectual.

En todas las secciones del informe debes aplicar tu conocimiento en neuroinclusión laboral: adapta el lenguaje, las recomendaciones y los ejemplos para que sean comprensibles, relevantes y motivadores para este colectivo. El informe debe redactarse en español de España, utilizando frases cortas y de fácil lectura, con un lenguaje profesional pero cercano. Evita metáforas complejas, sarcasmo o ambigüedades. Utiliza un tono directo, positivo y, cuando sea apropiado, proporciona instrucciones paso a paso. Utiliza únicamente los datos proporcionados, sin añadir información de relleno ni invenciones.

{feedback_previo}

**FORMATO DE SALIDA:**
• El informe debe generarse en formato Markdown para facilitar su visualización
• Utiliza encabezados (##, ###) para estructurar las secciones
• Emplea listas con viñetas para mejorar la legibilidad
• Si algún dato está ausente o es insuficiente, indícalo claramente
• No inventes información que no esté en los datos proporcionados
• Cuando no tengas datos suficientes para una sección, sugiere qué información adicional sería útil
• **IMPORTANTE**: Usa párrafos cortos (máximo 3-4 frases por párrafo) para facilitar la lectura
• **IMPORTANTE**: Estructura el contenido en listas y sublistas cuando sea posible
• **IMPORTANTE**: Evita párrafos muy largos que puedan causar problemas de visualización
• **IMPORTANTE**: En todas las listas numeradas, el número debe aparecer en la misma línea que el título o contenido, NO en una línea separada
• **IMPORTANTE**: Usa el formato "1. Título del elemento" en lugar de "1.\nTítulo del elemento"
• **IMPORTANTE**: Mantén coherencia en el formato de numeración en todo el documento

**TONO EMOCIONAL:**
• Mantén un equilibrio entre realismo y optimismo
• Reconoce los desafíos sin ser desalentador
• Celebra los logros y progresos, por pequeños que sean
• Utiliza un lenguaje motivador y constructivo, evitando generalizaciones y estereotipos

**Requisitos generales**
• Genera un informe extenso y completo, con un mínimo de 2.500 palabras.
• Cada sección debe contener al menos tres o cuatro párrafos detallados. No seas escueto ni superficial.
• Ofrece perspectivas de desarrollo a corto, medio y largo plazo.
• Incluye siempre ejemplos concretos y casos de uso aplicables.
• Proporciona recursos específicos, accionables y verificables. Puedes proporcionar enlaces a recursos útiles.
• Cita y referencia de manera específica los datos del CV en las secciones correspondientes.
• Mantén un enfoque positivo, empoderador y basado en evidencia, destacando fortalezas sin omitir áreas de mejora.

**Datos del candidato a analizar**
{perfil}

El informe debe seguir exactamente la siguiente estructura y contenido:

## 1. Resumen del perfil
• Presenta un resumen conciso y estructurado del candidato. Utiliza viñetas y subsecciones claras para detallar:
  o Datos personales básicos: nombre y otras características principales.
  o Preferencias laborales: áreas de interés, modalidad de trabajo preferida, disponibilidad, desplazamiento y adaptaciones necesarias.
  o Experiencia y nivel general de empleabilidad: ofrece una visión general de su experiencia profesional (cita fechas, empresas y puestos cuando existan) y elabora una valoración global de su empleabilidad.
  o Resumen del CV: cita específicamente la experiencia laboral, la formación académica y las habilidades técnicas del CV (incluyendo fechas, empresas, puestos, estudios, etc.).
  o Perfil de habilidades: resume las soft skills más destacadas con sus niveles (basándote en la sección "HABILIDADES SOFT EVALUADAS").

## 2. Análisis del CV
• Realiza una evaluación detallada del CV, citando los datos reales extraídos por el sistema de análisis inteligente. Debes incluir:

### Formación académica
• Describe los estudios cursados, titulaciones, fechas e instituciones extraídas del CV.
• Evalúa la relevancia de la formación para el mercado laboral actual.
• Cita específicamente cada elemento de formación detectado.

### Experiencia laboral
• Expón cada puesto de trabajo, empresa, fechas y tareas realizadas extraídas del CV.
• Analiza la transferibilidad de competencias adquiridas.
• Cita específicamente cada experiencia laboral detectada con sus detalles.

### Habilidades técnicas
• Menciona las herramientas, lenguajes o tecnologías utilizadas extraídas del CV.
• Evalúa su nivel de dominio y actualidad.
• Cita específicamente cada habilidad técnica detectada.

### Idiomas
• Incluye los idiomas y niveles extraídos del CV.
• Cita específicamente cada idioma detectado con su nivel.

### Proyectos y logros
• Describe los proyectos detectados en el CV.
• Analiza los logros y resultados cuantificables.
• Cita específicamente cada proyecto detectado.

### Análisis de estructura y calidad
• Valora la estructura, coherencia, claridad y diseño del CV basándote en el análisis automático.
• Incluye iconos o indicadores para representar formato, claridad, información clave y ortografía.
• Cita específicamente las fortalezas y debilidades detectadas en el análisis.

### Recomendaciones de mejora
• Proporciona recomendaciones personalizadas basadas en el análisis automático del CV.
• Ofrece ejemplos concretos para mejorar el CV, adaptarlo a diferentes empresas y resaltar habilidades relevantes.
• Cita específicamente las alertas y áreas de mejora detectadas.

## 3. Fortalezas (blandas y técnicas)
• Enumera las habilidades blandas con nivel "alto" identificadas en la sección de habilidades evaluadas y en el análisis del CV.
• Para cada fortaleza, describe brevemente cómo se manifiesta y ofrece ejemplos prácticos de cómo el candidato puede aplicarla en un entorno laboral.
• Incorpora también las fortalezas técnicas derivadas del CV, como experiencia relevante, logros profesionales o destrezas específicas.
• Ten en cuenta el nivel de confianza del candidato para reforzar su autoconfianza y validar sus percepciones.
• Cita específicamente las fortalezas detectadas en el análisis automático del CV.
• **FORMATO**: Usa listas numeradas con el formato "1. Nombre de la fortaleza" (número y título en la misma línea)

## 4. Áreas de mejora (blandas y técnicas) y consejos
• Selecciona hasta cuatro habilidades blandas con nivel "bajo" o "medio" de la sección de habilidades evaluadas.
• Describe cada área de mejora de forma comprensiva y ofrece consejos prácticos y accesibles (por ejemplo, pasos a seguir, recursos recomendados, vídeos, lecturas). Asegúrate de que estos consejos ayuden a construir confianza y a superar inseguridades.
• Incluye obligatoriamente las áreas de mejora identificadas en el análisis automático del CV.
• Distingue entre habilidades blandas y técnicas cuando corresponda, ofreciendo estrategias distintas para cada una.
• Cita específicamente las debilidades detectadas en el análisis automático del CV.
• **FORMATO**: Usa listas numeradas con el formato "1. Nombre del área de mejora" (número y título en la misma línea)

## 5. Sugerencias laborales
• Basándote en las preferencias laborales del candidato, los resultados de los minijuegos (sección "LOGS DE JUEGOS") y el análisis detallado del CV, sugiere:

### Entornos de trabajo ideales
• Colaborativo, autónomo, estructurado, flexible…, explicando por qué se adaptan a su perfil.
• **FORMATO**: Si usas listas numeradas, usa "1. Tipo de entorno" (número y título en la misma línea)

### Tipos de tareas recomendadas
• Estas recomendaciones se deben de basar en su experiencia, preferencias y fortalezas: tareas repetitivas, proyectos de resolución de problemas, trabajos con interacción social limitada o funciones de apoyo, respaldadas por su rendimiento y experiencia.
• **FORMATO**: Si usas listas numeradas, usa "1. Tipo de tarea" (número y título en la misma línea)

### Consejos de búsqueda de empleo
• Plataformas de búsqueda de empleo, plataformas inclusivas (sólo si el candidato indica que tiene certificado de discapacidad), búsqueda activa de empleo, estrategias de networking, preparación de entrevistas, teniendo en cuenta cómo gestiona la información y el estrés,etc.
• **FORMATO**: Si usas listas numeradas, usa "1. Consejo específico" (número y título en la misma línea)

### Adaptaciones específicas
• Recomendaciones sobre horarios flexibles, apoyos tecnológicos o ajustes en el puesto de trabajo que el candidato puede solicitar.
• **FORMATO**: Si usas listas numeradas, usa "1. Adaptación específica" (número y título en la misma línea)

• Cita específicamente la experiencia y formación extraída del CV para justificar cada sugerencia.

**INSTRUCCIONES FINALES DE FORMATO:**
• Asegúrate de que TODAS las listas numeradas tengan el número y el contenido en la misma línea
• Ejemplo correcto: "1. Resiliencia y flexibilidad (80%)"
• Ejemplo incorrecto: "1.\nResiliencia y flexibilidad (80%)"
• Mantén esta coherencia en todo el documento
"""

    # Llamada a la API con timeout extendido
    try:
        print(f"🤖 Enviando prompt a Azure OpenAI (deployment: {DEPLOYMENT})...")
        respuesta = client.chat.completions.create(
            model=DEPLOYMENT,  # type: ignore
            messages=[
                {"role": "system", "content": "Eres un psicólogo laboral experto en neuroinclusión, con más de 15 años de experiencia en orientación profesional para personas neurodivergentes. Tienes formación en psicología clínica, neuropsicología y empleabilidad. Tu enfoque es científico, empático y basado en evidencia. Siempre consideras las fortalezas únicas de cada persona y propones adaptaciones prácticas para maximizar su potencial laboral. IMPORTANTE: Genera informes EXTENSOS y DETALLADOS, no seas escueto."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=8000,
            temperature=0.7
        )
        
        contenido = respuesta.choices[0].message.content or ""
        print(f"✅ Informe generado exitosamente ({len(contenido)} caracteres)")
        return contenido
        
    except Exception as e:
        error_msg = f"❌ Error en la llamada a Azure OpenAI: {str(e)}"
        if "DeploymentNotFound" in str(e):
            error_msg += f"\n\nEl deployment '{DEPLOYMENT}' no existe en tu recurso de Azure OpenAI."
            error_msg += "\n\nPara solucionarlo:"
            error_msg += "\n1. Ve a tu recurso de Azure OpenAI en Azure Portal"
            error_msg += "\n2. Ve a 'Model deployments'"
            error_msg += "\n3. Crea un nuevo deployment con un modelo disponible (gpt-35-turbo, gpt-4, etc.)"
            error_msg += "\n4. Actualiza AZURE_OPENAI_DEPLOYMENT en tu archivo .env"
        elif "authentication" in str(e).lower() or "unauthorized" in str(e).lower():
            error_msg += "\n\nError de autenticación. Verifica que:"
            error_msg += "\n1. La API Key sea correcta"
            error_msg += "\n2. Tengas permisos para usar el deployment"
        elif "timeout" in str(e).lower():
            error_msg += "\n\nTimeout en la llamada. El prompt puede ser muy largo."
            error_msg += "\nIntenta con un prompt más corto o aumenta el timeout."
        
        raise RuntimeError(error_msg)
