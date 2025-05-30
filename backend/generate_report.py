import os
from openai import AzureOpenAI
from dotenv import load_dotenv

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

def generar_informe(candidato):
    prompt = f"""
    Eres un orientador laboral experto en neurodiversidad y psicología. Analiza el siguiente perfil y redacta un informe profesional de empleabilidad, incluyendo:
    - Resumen del perfil (datos, experiencia, preferencias).
    - Conclusiones generales del CV y minijuegos.
    - Fortalezas detectadas.
    - Áreas de mejora (con consejos personalizados).
    - Orientación laboral específica.

    Perfil del candidato: {candidato}
    """

    respuesta = client.chat.completions.create(
        model=DEPLOYMENT,
        messages=[{"role": "system", "content": "Eres un orientador laboral y psicólogo especializado."},
                  {"role": "user", "content": prompt}],
        max_tokens=1000
    )
    return respuesta.choices[0].message.content

# Ejemplo de uso:
if __name__ == "__main__":
    datos_candidato = """
    Nombre: María Pérez
    Preferencias: Jornada parcial, remoto, sector administrativo. 
    Resultados minijuegos: Comunicación alta, liderazgo medio, creatividad alta, resolución baja...
    Resumen CV: 5 años experiencia en administración y atención al cliente, estudios de FP...
    """
    informe = generar_informe(datos_candidato)
    print(informe)
