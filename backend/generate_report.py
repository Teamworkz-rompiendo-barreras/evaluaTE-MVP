# backend/generate_report.py

import os
from openai import AzureOpenAI
from dotenv import load_dotenv

# ─── Cargamos variables de entorno ───
load_dotenv()  # Busca un archivo .env en esta carpeta

API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT")
API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")

if not all([API_KEY, ENDPOINT, DEPLOYMENT, API_VERSION]):
    raise RuntimeError("Faltan variables de entorno de Azure OpenAI")

# Cliente de Azure OpenAI
client = AzureOpenAI(
    api_key=API_KEY,
    api_version=API_VERSION,
    azure_endpoint=ENDPOINT
)

def generar_informe(perfil: str) -> str:
    """
    Envía el prompt a Azure OpenAI y devuelve el texto completo del informe.
    `perfil` debe contener todo: datos del formulario, scores de softskills y texto del CV.
    """

    prompt = f"""
Eres un orientador laboral experto en empleabilidad, neurodiversidad y discapacidad intelectual.
Tu tarea es analizar el siguiente PERFIL COMPLETO (datos, resultados de mini‐juegos y texto del CV) y generar un INFORME PROFESIONAL DE EMPLEABILIDAD, estructurado y redactado en lenguaje claro, directo, accesible y humano.

---
INFORMACIÓN QUE TIENES:
{perfil}

---
AL ENTREGAR, ESTRUCTURA tu respuesta EXACTAMENTE así (con mayúsculas en cada título):
1. RESUMEN PERSONAL:
(1 párrafo breve con descripción de perfil, experiencia, intereses y disponibilidad)

2. FORTALEZAS:
- (lista de 3–5 fortalezas detectadas, relacionadas con habilidades y actitudes laborales)

3. OPORTUNIDADES DE MEJORA:
- (lista de 2–4, con sugerencias muy breves para avanzar)

4. ORIENTACIÓN LABORAL PERSONALIZADA:
(2–3 propuestas concretas de empleos compatibles con su perfil y entorno)

5. CONCLUSIÓN POSITIVA:
(un párrafo final motivador que refuerce su potencial y próxima acción recomendada)

INSTRUCCIONES PARA REDACCIÓN:
- Lenguaje respetuoso y claro, sin tecnicismos.
- Redactado para persona con posibles dificultades cognitivas o comprensión.
- Frases cortas, tono alentador y estilo profesional.
    """
    # Llamada a la API
    respuesta = client.chat.completions.create(
        model=DEPLOYMENT,
        messages=[
            {"role": "system", "content": "Eres un psicólogo laboral experto en orientación, neurodiversidad y accesibilidad cognitiva."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=2000
    )

    return respuesta.choices[0].message.content
