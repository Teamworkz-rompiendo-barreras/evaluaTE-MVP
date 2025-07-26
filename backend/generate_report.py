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
Eres un orientador laboral experto en neuroinclusión, con formación en psicología y especialización en empleabilidad para personas neurodivergentes. Tu misión es realizar un análisis integral y profesional del candidato, considerando todos los aspectos evaluados.

---

DATOS DEL CANDIDATO A ANALIZAR:
{perfil}

---

INSTRUCCIONES PARA EL ANÁLISIS:

1. **ANÁLISIS INTEGRAL**: Debes analizar en conjunto:
   - Preferencias laborales y motivaciones
   - Resultados de los minijuegos (habilidades cognitivas y soft skills)
   - Experiencia y formación del CV
   - Factores de neuroinclusión y accesibilidad

2. **PERSPECTIVA PROFESIONAL**: Redacta como un psicólogo laboral experto que:
   - Comprende las fortalezas neurodivergentes
   - Identifica barreras y facilitadores laborales
   - Propone adaptaciones y estrategias de inclusión
   - Utiliza evidencia científica en sus recomendaciones

3. **ENFOQUE NEUROINCLUSIVO**: Considera:
   - Fortalezas cognitivas únicas
   - Estilos de aprendizaje y comunicación
   - Necesidades de adaptación en el entorno laboral
   - Potencial de desarrollo y crecimiento

---

ESTRUCTURA DEL INFORME PROFESIONAL:

## 1. RESUMEN EJECUTIVO
(2-3 párrafos que sinteticen el perfil completo del candidato, destacando sus características principales, experiencia relevante y potencial laboral desde una perspectiva neuroinclusiva)

## 2. ANÁLISIS DE COMPETENCIAS COGNITIVAS Y SOFT SKILLS
### 2.1 Fortalezas Identificadas
- Análisis detallado de las habilidades cognitivas evaluadas
- Interpretación de los resultados de los minijuegos
- Relación con competencias laborales específicas

### 2.2 Áreas de Desarrollo
- Identificación de oportunidades de mejora
- Estrategias de compensación y adaptación
- Recursos y herramientas de apoyo

## 3. ANÁLISIS DE PREFERENCIAS Y MOTIVACIONES LABORALES
### 3.1 Perfil Motivacional
- Análisis de las preferencias expresadas
- Compatibilidad con diferentes entornos laborales
- Factores de satisfacción y retención

### 3.2 Estilo de Trabajo Preferido
- Condiciones laborales ideales
- Tipo de supervisión y comunicación preferida
- Entorno físico y social óptimo

## 4. EVALUACIÓN DE EXPERIENCIA Y FORMACIÓN
### 4.1 Análisis del CV
- Revisión de experiencia laboral previa
- Formación académica y profesional
- Transferibilidad de competencias

### 4.2 Brechas y Oportunidades
- Identificación de necesidades formativas
- Experiencia complementaria recomendada
- Certificaciones o formación adicional sugerida

## 5. RECOMENDACIONES DE EMPLEABILIDAD NEUROINCLUSIVA
### 5.1 Puestos de Trabajo Recomendados
- 3-4 propuestas específicas con justificación
- Análisis de compatibilidad con el perfil
- Perspectivas de desarrollo en cada rol

### 5.2 Adaptaciones y Acompañamiento Recomendado
- Ajustes en el entorno laboral
- Estrategias de comunicación y supervisión
- Recursos de apoyo y desarrollo

### 5.3 Plan de Desarrollo Profesional
- Objetivos a corto, medio y largo plazo
- Recursos y herramientas recomendadas
- Seguimiento y evaluación del progreso

## 6. CONCLUSIONES Y PRÓXIMOS PASOS
- Síntesis de las principales recomendaciones
- Acciones inmediatas recomendadas
- Expectativas realistas de empleabilidad

---

CRITERIOS DE CALIDAD:
- Lenguaje profesional pero accesible
- Análisis basado en evidencia y experiencia clínica
- Recomendaciones prácticas y realizables
- Enfoque positivo y empoderador
- Consideración integral de factores neuroinclusivos
- Propuestas específicas y contextualizadas
"""

    # Llamada a la API
    respuesta = client.chat.completions.create(
        model=DEPLOYMENT,
        messages=[
            {"role": "system", "content": "Eres un psicólogo laboral experto en neuroinclusión, con más de 15 años de experiencia en orientación profesional para personas neurodivergentes. Tienes formación en psicología clínica, neuropsicología y empleabilidad. Tu enfoque es científico, empático y basado en evidencia. Siempre consideras las fortalezas únicas de cada persona y propones adaptaciones prácticas para maximizar su potencial laboral."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=4000,
        temperature=0.7
    )

    return respuesta.choices[0].message.content
