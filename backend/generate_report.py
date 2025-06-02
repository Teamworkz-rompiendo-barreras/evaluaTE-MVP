import os
from openai import AzureOpenAI
from dotenv import load_dotenv
import fitz  # PyMuPDF

# Cargar variables de entorno del .env
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

def leer_texto_cv(ruta_pdf: str) -> str:
    """Extrae el texto plano de un archivo PDF"""
    if not os.path.exists(ruta_pdf):
        return "CV no disponible o no encontrado."
    
    texto = ""
    try:
        with fitz.open(ruta_pdf) as doc:
            for pagina in doc:
                texto += pagina.get_text()
    except Exception as e:
        texto = f"Error al leer el CV: {e}"
    
    return texto.strip()

def generar_informe(datos: dict) -> dict:
    """Genera un informe completo y estructurado basado en los datos del formulario + CV + minijuegos"""

    nombre = f"{datos.get('nombre', '')} {datos.get('apellidos', '')}".strip()
    email = datos.get("email", "")
    whatsapp = datos.get("whatsapp", "")
    ruta_cv = datos.get("ruta_cv", "")
    resultados = datos.get("resultados_minijuegos", "")

    texto_cv = leer_texto_cv(ruta_cv)

    prompt = f"""
Eres un orientador laboral experto en psicología, empleo y neurodiversidad. A partir del perfil de una persona neurodivergente o con discapacidad intelectual, redacta un informe profesional de empleabilidad estructurado en las siguientes secciones:

1. Resumen del perfil (nombre, contacto, perfil general y potencial profesional).
2. Fortalezas detectadas (extraídas del CV y resultados de autoevaluación).
3. Áreas de mejora con recomendaciones personalizadas.
4. Orientación laboral personalizada según su perfil y preferencias.
5. Conclusión motivadora y positiva.

Utiliza un lenguaje claro, profesional y empático. No repitas literalmente los datos. Presenta cada apartado por separado. No utilices markdown ni símbolos extraños. 

Datos disponibles:
- Nombre completo: {nombre}
- Email: {email}
- WhatsApp: {whatsapp}
- Resultados de autoevaluación (minijuegos): {resultados}
- Contenido del CV: {texto_cv}
"""

    respuesta = client.chat.completions.create(
        model=DEPLOYMENT,
        messages=[
            {"role": "system", "content": "Eres un psicólogo experto en empleabilidad y orientación laboral neurodivergente."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=1800,
        temperature=0.7
    )

    texto = respuesta.choices[0].message.content.strip()

    # Por ahora devolvemos todo como un bloque en "resumen"
    # En la siguiente versión podemos aplicar NLP para separar las secciones automáticamente
    return {
        "resumen": texto,
        "fortalezas": [],
        "areas_mejora": [],
        "orientacion": "",
        "conclusion": ""
    }

# Ejemplo de prueba manual
if __name__ == "__main__":
    ejemplo = {
        "nombre": "Ester",
        "apellidos": "Pérez Ribada",
        "email": "ester@ejemplo.com",
        "whatsapp": "666666666",
        "ruta_cv": "uploads/ester_cv.pdf",
        "resultados_minijuegos": "Comunicación alta, resolución media, liderazgo bajo"
    }

    informe = generar_informe(ejemplo)
    print(informe["resumen"])