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

def generar_informe(perfil: str) -> str:
    """
    Envía el prompt a Azure OpenAI y devuelve el texto completo del informe.
    `perfil` debe contener todo: datos del formulario, scores de softskills y texto del CV.
    """

    prompt = f"""
Eres un orientador laboral sénior con estudios en psicología y experto en neuroinclusión laboral. Tu misión es generar un informe de empleabilidad personalizado, preciso, riguroso y profesional para personas neurodivergentes (autismo, TDAH, dislexia, Tourette, etc.) y/o con discapacidad intelectual.

En todas las secciones del informe debes aplicar tu conocimiento en neuroinclusión laboral: adapta el lenguaje, las recomendaciones y los ejemplos para que sean comprensibles, relevantes y motivadores para este colectivo. El informe debe redactarse en español de España, utilizando frases cortas y de fácil lectura, con un lenguaje profesional pero cercano. Evita metáforas complejas, sarcasmo o ambigüedades. Utiliza un tono directo, positivo y, cuando sea apropiado, proporciona instrucciones paso a paso. Utiliza únicamente los datos proporcionados, sin añadir información de relleno ni invenciones.

**FORMATO DE SALIDA:**
• El informe debe generarse en formato Markdown para facilitar su visualización
• Utiliza encabezados (##, ###) para estructurar las secciones
• Emplea listas con viñetas para mejorar la legibilidad
• Si algún dato está ausente o es insuficiente, indícalo claramente
• No inventes información que no esté en los datos proporcionados
• Cuando no tengas datos suficientes para una sección, sugiere qué información adicional sería útil

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
• Proporciona recursos específicos, accionables y verificables.
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
• Realiza una evaluación detallada del CV, citando los datos reales de la sección "ANÁLISIS DETALLADO DEL CV". Debes incluir:
  o Formación académica: describe los estudios cursados, titulaciones, fechas e instituciones.
  o Experiencia laboral: expón cada puesto de trabajo, empresa, fechas y tareas realizadas (cita textualmente los datos cuando estén disponibles).
  o Habilidades técnicas: menciona las herramientas, lenguajes o tecnologías utilizadas.
  o Idiomas: incluye los idiomas y niveles si aparecen en el CV.
  o Análisis visual: valora la estructura, coherencia, claridad y diseño del CV. Incluye iconos o indicadores (por ejemplo, estrellas) para representar formato, claridad, información clave y ortografía.
  o Sección de experiencia y personalización: evalúa cómo se presenta la experiencia laboral y ofrece recomendaciones para personalizar el CV según sectores o puestos de interés.
  o Ortografía: comenta la calidad ortográfica, destacando aciertos o posibles correcciones.
• Proporciona recomendaciones personalizadas y ejemplos concretos para mejorar el CV, adaptarlo a diferentes empresas y resaltar habilidades relevantes.

## 3. Fortalezas (blandas y técnicas)
• Enumera las habilidades blandas con nivel "alto" identificadas en la sección de habilidades evaluadas y en el análisis del CV.
• Para cada fortaleza, describe brevemente cómo se manifiesta y ofrece ejemplos prácticos de cómo el candidato puede aplicarla en un entorno laboral.
• Incorpora también las fortalezas técnicas derivadas del CV, como experiencia relevante, logros profesionales o destrezas específicas.
• Ten en cuenta el nivel de confianza del candidato para reforzar su autoconfianza y validar sus percepciones.

## 4. Áreas de mejora (blandas y técnicas) y consejos
• Selecciona hasta cuatro habilidades blandas con nivel "bajo" o "medio" de la sección de habilidades evaluadas.
• Describe cada área de mejora de forma comprensiva y ofrece consejos prácticos y accesibles (por ejemplo, pasos a seguir, recursos recomendados, vídeos, lecturas). Asegúrate de que estos consejos ayuden a construir confianza y a superar inseguridades.
• Incluye obligatoriamente las áreas de mejora identificadas en el análisis del CV (por ejemplo, ausencia de verbos de acción, falta de cuantificación de logros, necesidad de formación adicional, etc.).
• Distingue entre habilidades blandas y técnicas cuando corresponda, ofreciendo estrategias distintas para cada una.

## 5. Sugerencias laborales
• Basándote en las preferencias laborales del candidato, los resultados de los minijuegos (sección "LOGS DE JUEGOS") y el análisis del CV, sugiere:
  o Entornos de trabajo ideales: colaborativo, autónomo, estructurado, flexible…, explicando por qué se adaptan a su perfil.
  o Tipos de tareas recomendadas: Estas recomendaciones se deben de basar en su experiencia, preferencias y fortalezas: tareas repetitivas, proyectos de resolución de problemas, trabajos con interacción social limitada o funciones de apoyo, respaldadas por su rendimiento y experiencia.
  o Consejos de búsqueda de empleo: plataformas de búsqueda de empleo, plataformas inclusivas (sólo si tiene certificado de discapacidad), búsqueda activa de empleo, estrategias de networking, preparación de entrevistas, teniendo en cuenta cómo gestiona la información y el estrés,etc.
  o Adaptaciones específicas: recomendaciones sobre horarios flexibles, apoyos tecnológicos o ajustes en el puesto de trabajo que el candidato puede solicitar.
• Cita específicamente la experiencia y formación del CV para justificar cada sugerencia.

## 6. Próximos pasos
• Propón acciones de formación relevantes basadas en las áreas de mejora y preferencias laborales (cursos, certificaciones, talleres).
• Aconseja crear un perfil de LinkedIn si no lo tienen creado. Añade algún enlace donde puedan aprender a crearse ese perfil
• Incluye un plan de acción concreto con fechas, objetivos específicos y tareas semanales.
• Finaliza con una frase explicando que ese informe ha sido realizado de manera personalizada para ajustarlo al perfil del candidato.
• Referencia su experiencia y formación para personalizar los consejos y priorizar las próximas acciones.

## 7. Recursos y apoyo adicional
• Recomienda herramientas tecnológicas de apoyo que puedan facilitar el desempeño laboral (por ejemplo, Trello para organizar tareas, Grammarly para corregir textos).
• Incluye contactos o programas de orientadores laborales especializados en neuroinclusión, indicando cómo acceder a ellos.
• Lista organizaciones y asociaciones específicas que ofrecen apoyo para personas neurodivergentes en el ámbito laboral.
• Enfatiza el uso de estos recursos como parte del plan de desarrollo personal y profesional.

**Criterios de calidad obligatorios**
• Emplea un lenguaje profesional pero accesible, sin jerga técnica compleja.
• Aporta análisis basados en evidencia y experiencia en neuroinclusión.
• Ofrece recomendaciones prácticas, realizables y contextualizadas.
• Mantén un enfoque positivo y empoderador, destacando fortalezas y sugiriendo mejoras desde la motivación.
• Considera integralmente los factores neuroinclusivos y personaliza tus consejos.
• Evita generalizaciones y estereotipos; sé específico y preciso.
• Cada sección debe tener al menos 3–4 párrafos detallados y contribuir al mínimo de 2.500 palabras.
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
