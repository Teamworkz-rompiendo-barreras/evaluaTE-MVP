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
    Eres un orientador/a laboral experto/a en psicología, neurodiversidad y discapacidad intelectual. Tu misión es redactar un informe de empleabilidad profesional, empático, claro y útil para una persona neurodivergente o con discapacidad intelectual, a partir de los siguientes datos:

{candidato}

Redacta el informe como si fuera un documento formal de orientación laboral, dividido en las siguientes secciones, cada una con su título claro, redactadas con un tono humano, profesional y respetuoso. Evita tecnicismos complejos y utiliza frases cortas y comprensibles.

1. **Resumen del perfil**  
Breve descripción general de la persona candidata (nombre, experiencia, formación, preferencias laborales, fortalezas destacadas...).

2. **Fortalezas detectadas**  
Menciona de forma clara y concreta las principales habilidades o capacidades de la persona, basándote en los resultados de los minijuegos y la revisión del CV. Usa frases breves en forma de lista o párrafo estructurado.

3. **Oportunidades de mejora**  
Identifica áreas que pueden reforzarse. Hazlo de forma constructiva y empática, aportando siempre consejos útiles, accesibles y sin juicios.

4. **Orientación laboral personalizada**  
Sugiérele tipos de empleo o entornos laborales donde podría destacar y sentirse a gusto. Ten en cuenta sus preferencias, fortalezas y nivel de apoyo.

5. **Conclusión**  
Cierra el informe con un mensaje motivador, profesional y positivo que refuerce su valor y capacidad de crecimiento. Reafirma su potencial.

Este informe será utilizado por la persona candidata y por entidades de empleo que le acompañan, por lo que debe ser claro, útil y respetuoso.

No te salgas de este formato. Escribe cada apartado con título y contenido separado.
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
