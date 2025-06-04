import os
from openai import AzureOpenAI
from dotenv import load_dotenv

# Cargar variables de entorno
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

def generar_informe(perfil):
    prompt = f"""
Eres un orientador laboral experto en empleabilidad, neurodiversidad y discapacidad intelectual.
Tu tarea es analizar el perfil que te damos a continuación y generar un INFORME PROFESIONAL DE EMPLEABILIDAD, estructurado y redactado en lenguaje claro, directo, accesible y humano.

El informe debe incluir las siguientes SECCIONES diferenciadas:
1. RESUMEN PERSONAL (1 párrafo breve con descripción de perfil, experiencia, intereses y disponibilidad)
2. FORTALEZAS (una lista de entre 3 y 5 fortalezas detectadas, relacionadas con habilidades y actitudes laborales)
3. OPORTUNIDADES DE MEJORA (entre 2 y 4, con sugerencias breves para avanzar)
4. ORIENTACIÓN LABORAL PERSONALIZADA (con 2-3 propuestas concretas de empleos compatibles con su perfil y entorno)
5. CONCLUSIÓN POSITIVA (mensaje final motivador que refuerce su potencial y próxima acción recomendada)

El lenguaje debe ser:
- Respetuoso y claro, sin tecnicismos.
- Redactado para una persona con posibles dificultades cognitivas o de comprensión.
- Con frases breves, tono alentador y estilo profesional.

Este es el perfil a analizar:

{perfil}
"""

    respuesta = client.chat.completions.create(
        model=DEPLOYMENT,
        messages=[
            {"role": "system", "content": "Eres un psicólogo laboral experto en orientación, neurodiversidad y accesibilidad cognitiva."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=1800
    )

    return respuesta.choices[0].message.content


# Prueba local
if __name__ == "__main__":
    perfil_prueba = """
    Nombre: María Pérez
    Email: maria.perez@email.com
    WhatsApp: 600123123
    Jornada: Parcial
    Modalidad: Remoto
    Puesto deseado: Auxiliar administrativa
    CV: 5 años de experiencia como recepcionista y apoyo en tareas administrativas. Formación en FP de Gestión Administrativa. Buenas habilidades interpersonales y manejo de herramientas ofimáticas.
    Resultados de soft skills:
    Comunicación: alta
    Trabajo en equipo: media
    Gestión del tiempo: baja
    Resolución de problemas: alta
    Adaptabilidad: media
    """

    resultado = generar_informe(perfil_prueba)
    print(resultado)
