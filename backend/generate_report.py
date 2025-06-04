import os
from openai import AzureOpenAI
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

API_KEY     = os.getenv("AZURE_OPENAI_API_KEY")
ENDPOINT    = os.getenv("AZURE_OPENAI_ENDPOINT")
DEPLOYMENT  = os.getenv("AZURE_OPENAI_DEPLOYMENT")
API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")

client = AzureOpenAI(
    api_key       = API_KEY,
    api_version   = API_VERSION,
    azure_endpoint= ENDPOINT
)

def generar_informe(perfil):
    """
    Genera un texto con delimitadores muy claros para luego parsearlo:
    ---SECCIÓN-1---
    (RESUMEN PERSONAL)
    ---SECCIÓN-2---
    (FORTALEZAS, lista con “*”)
    ---SECCIÓN-3---
    (OPORTUNIDADES DE MEJORA, lista con “*”)
    ---SECCIÓN-4---
    (ORIENTACIÓN LABORAL PERSONALIZADA)
    ---SECCIÓN-5---
    (CONCLUSIÓN POSITIVA)
    """

    prompt = f"""
Eres un orientador laboral experto en empleabilidad, neurodiversidad y discapacidad intelectual. 
Genera un INFORME PROFESIONAL DE EMPLEABILIDAD, con lenguaje claro, directo, accesible y humano.

**Instrucciones de formato**: El informe DEVOLVERÁSE estrictamente de la siguiente forma:

---SECCIÓN-1---
RESUMEN PERSONAL: Un único párrafo breve (2–3 líneas).

---SECCIÓN-2---
FORTALEZAS (entre 3 y 5 items): Cada fortaleza debe ir precedida de un asterisco (*) y un espacio. Ejemplo:
* Buena comunicación
* Trabajo en equipo
* …

---SECCIÓN-3---
OPORTUNIDADES DE MEJORA (entre 2 y 4 items): Cada punto con un asterisco (*) y un espacio. Ejemplo:
* Gestionar mejor el tiempo
* …

---SECCIÓN-4---
ORIENTACIÓN LABORAL PERSONALIZADA: Dos o tres recomendaciones de empleos compatibles (formato párrafo).

---SECCIÓN-5---
CONCLUSIÓN POSITIVA: Un párrafo motivador de 2–3 líneas que refuerce el potencial y recomiende la próxima acción.

El lenguaje debe ser:
- Respetuoso, claro y sin tecnicismos.
- Redactado para una persona con posibles dificultades cognitivas.
- Frases muy cortas, tono alentador y estilo profesional.

Este es el perfil a analizar (nombres de campo y valores):
{perfil}
"""
    respuesta = client.chat.completions.create(
        model    = DEPLOYMENT,
        messages = [
            {"role": "system", "content": "Eres un psicólogo laboral experto en orientación, neurodiversidad y accesibilidad cognitiva."},
            {"role": "user",   "content": prompt}
        ],
        max_tokens = 1800
    )

    return respuesta.choices[0].message.content


# Prueba local (opcional)
if __name__ == "__main__":
    perfil_prueba = """
    Nombre: María Pérez
    Email: maria.perez@email.com
    WhatsApp: 600123123
    Jornada: Parcial
    Modalidad: Remoto
    Puesto deseado: Auxiliar administrativa
    CV: 5 años de experiencia como recepcionista y apoyo en tareas administrativas. Formación en FP.
    Resultados de soft skills:
    Comunicación: alta
    Trabajo en equipo: media
    Gestión del tiempo: baja
    Resolución de problemas: alta
    Adaptabilidad: media
    """
    resultado = generar_informe(perfil_prueba)
    print(resultado)
