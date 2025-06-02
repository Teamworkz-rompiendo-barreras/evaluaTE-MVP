import os
import pdfplumber
from openai import AzureOpenAI
from dotenv import load_dotenv

# Cargar claves del .env
load_dotenv()
API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT")
API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")

client = AzureOpenAI(
    api_key=API_KEY,
    api_version=API_VERSION,
    azure_endpoint=ENDPOINT
)

def leer_cv(path_cv):
    """Extrae el texto completo de un CV en PDF."""
    texto = ""
    try:
        with pdfplumber.open(path_cv) as pdf:
            for pagina in pdf.pages:
                texto += pagina.extract_text() + "\n"
    except Exception as e:
        texto = "No se pudo leer el CV correctamente."
    return texto.strip()

def generar_informe(candidato):
    """Genera un informe profesional estructurado con IA."""

    # Extraer texto del CV
    ruta_cv = candidato.get("ruta_cv", "")
    texto_cv = leer_cv(ruta_cv) if ruta_cv else "CV no disponible."

    # Resultados de minijuegos (puedes expandirlo cuando estén disponibles)
    resultados_minijuegos = candidato.get("resultados_minijuegos", "Sin resultados disponibles.")

    # Construir perfil completo
    perfil = f"""
    Nombre: {candidato.get('nombre', '')} {candidato.get('apellidos', '')}
    Email: {candidato.get('email', '')}
    WhatsApp: {candidato.get('whatsapp', '')}
    Resultados de minijuegos: {resultados_minijuegos}
    CV: {texto_cv}
    """

    # Prompt para solicitar informe profesional estructurado
    prompt = f"""
    Actúa como orientador/a laboral experto/a en neurodiversidad y discapacidad intelectual. Redacta un informe de empleabilidad profesional, claro, cálido y útil, en formato JSON con los siguientes campos:

    {{
        "resumen": "...",
        "fortalezas": ["...", "..."],
        "areas_mejora": ["...", "..."],
        "orientacion": "...",
        "conclusion": "..."
    }}

    Utiliza frases sencillas, accesibles y positivas, dirigidas tanto a la persona candidata como a profesionales que la acompañan. Evita lenguaje robótico. Este es el perfil a evaluar:

    {perfil}
    """

    respuesta = client.chat.completions.create(
        model=DEPLOYMENT,
        messages=[
            {"role": "system", "content": "Eres un orientador/a laboral experto/a en neurodiversidad."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=1500,
        temperature=0.7
    )

    contenido = respuesta.choices[0].message.content

    try:
        # Evaluamos si la respuesta es un JSON válido (aquí puedes usar json.loads si prefieres)
        if contenido.strip().startswith("{"):
            import json
            return json.loads(contenido)
        else:
            return {
                "resumen": contenido,
                "fortalezas": [],
                "areas_mejora": [],
                "orientacion": "",
                "conclusion": ""
            }
    except Exception:
        return {
            "resumen": contenido,
            "fortalezas": [],
            "areas_mejora": [],
            "orientacion": "",
            "conclusion": ""
        }
