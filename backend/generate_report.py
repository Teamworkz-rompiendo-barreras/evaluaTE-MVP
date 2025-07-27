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
Eres un orientador laboral experto en neuroinclusión, con formación en psicología y especialización en empleabilidad para personas neurodivergentes. Conocimiento actualizado del marco de competencias WEF 2025. Tu misión es realizar un análisis integral y PROFUNDAMENTE DETALLADO del candidato, considerando todos los aspectos evaluados.

IMPORTANTE: Debes generar un informe EXTENSO y COMPLETO. Cada sección debe tener al menos 3-4 párrafos detallados. NO seas escueto ni superficial.

CRÍTICO: Si algún dato no está disponible (como análisis de CV o logs de juegos), NO menciones esta limitación en el informe. En su lugar, enfócate en los datos disponibles y proporciona análisis basado en la información que sí tienes. El informe debe ser profesional y completo, sin referencias a datos faltantes.

---

DATOS DEL CANDIDATO A ANALIZAR:
{perfil}

---

INSTRUCCIONES PARA EL ANÁLISIS:

1. **ANÁLISIS INTEGRAL Y PROFUNDO**: Debes analizar en conjunto:
   - Preferencias laborales y motivaciones (con análisis psicológico)
   - Resultados de los minijuegos (interpretación detallada de cada habilidad)
   - Experiencia y formación del CV (análisis crítico y prospectivo)
   - Factores de neuroinclusión y accesibilidad (consideraciones específicas)

2. **PERSPECTIVA PROFESIONAL EXPERTA**: Redacta como un psicólogo laboral senior que:
   - Comprende las fortalezas neurodivergentes (con ejemplos específicos)
   - Identifica barreras y facilitadores laborales (con estrategias concretas)
   - Propone adaptaciones y estrategias de inclusión (detalladas y prácticas)
   - Utiliza evidencia científica en sus recomendaciones (con referencias)

3. **ENFOQUE NEUROINCLUSIVO COMPLETO**: Considera:
   - Fortalezas cognitivas únicas (con ejemplos de aplicación laboral)
   - Estilos de aprendizaje y comunicación (con estrategias específicas)
   - Necesidades de adaptación en el entorno laboral (con propuestas concretas)
   - Potencial de desarrollo y crecimiento (con roadmap detallado)

---

ESTRUCTURA DEL INFORME PROFESIONAL DETALLADO:

## 1. RESUMEN EJECUTIVO
(4-5 párrafos que sinteticen el perfil completo del candidato, destacando sus características principales, experiencia relevante, fortalezas únicas, áreas de mejora y potencial laboral desde una perspectiva neuroinclusiva. Incluir análisis de compatibilidad con el mercado laboral actual)

## 2. ANÁLISIS DETALLADO DE COMPETENCIAS COGNITIVAS Y SOFT SKILLS
### 2.1 Fortalezas Identificadas
- Análisis profundo de cada habilidad cognitiva evaluada (mínimo 2 párrafos por habilidad)
- Interpretación detallada de los resultados de los minijuegos
- Relación específica con competencias laborales demandadas
- Ejemplos de cómo estas fortalezas se traducen en valor laboral

### 2.2 Áreas de Desarrollo y Estrategias
- Identificación detallada de oportunidades de mejora (con análisis de impacto)
- Estrategias de compensación y adaptación específicas
- Recursos y herramientas de apoyo concretos
- Plan de acción para el desarrollo de cada área

## 3. ANÁLISIS COMPLETO DE PREFERENCIAS Y MOTIVACIONES LABORALES
### 3.1 Perfil Motivacional Profundo
- Análisis psicológico de las preferencias expresadas
- Compatibilidad detallada con diferentes entornos laborales
- Factores de satisfacción y retención específicos
- Análisis de alineación con valores personales

### 3.2 Estilo de Trabajo Preferido y Adaptaciones
- Condiciones laborales ideales (con justificación)
- Tipo de supervisión y comunicación preferida (con ejemplos)
- Entorno físico y social óptimo (con especificaciones)
- Estrategias de adaptación para diferentes entornos

## 4. EVALUACIÓN COMPREHENSIVA DE EXPERIENCIA Y FORMACIÓN
### 4.1 Análisis Crítico del CV
- Revisión detallada de experiencia laboral previa (con análisis de transferibilidad)
- Formación académica y profesional (con evaluación de relevancia actual)
- Transferibilidad de competencias a nuevos contextos
- Identificación de logros y contribuciones significativas

### 4.2 Brechas Identificadas y Oportunidades de Desarrollo
- Identificación detallada de necesidades formativas (con priorización)
- Experiencia complementaria recomendada (con timeline)
- Certificaciones o formación adicional sugerida (con justificación)
- Estrategias para cerrar brechas de competencias

## 5. RECOMENDACIONES ESPECÍFICAS DE EMPLEABILIDAD NEUROINCLUSIVA
### 5.1 Puestos de Trabajo Recomendados (MÍNIMO 4-5 ROLES)
- Propuestas específicas con justificación detallada
- Análisis de compatibilidad con el perfil (punto por punto)
- Perspectivas de desarrollo en cada rol (corto, medio y largo plazo)
- Requisitos específicos y preparación necesaria

### 5.2 Adaptaciones y Acompañamiento Recomendado
- Ajustes específicos en el entorno laboral (con ejemplos prácticos)
- Estrategias de comunicación y supervisión detalladas
- Recursos de apoyo y desarrollo específicos
- Plan de acompañamiento durante la transición laboral

### 5.3 Plan de Desarrollo Profesional Detallado
- Objetivos específicos a corto plazo (3-6 meses)
- Objetivos a medio plazo (6-18 meses)
- Objetivos a largo plazo (18+ meses)
- Recursos y herramientas recomendadas (con enlaces y descripciones)
- Métricas de seguimiento y evaluación del progreso

## 6. CONCLUSIONES COMPREHENSIVAS Y PRÓXIMOS PASOS
- Síntesis detallada de las principales recomendaciones
- Acciones inmediatas recomendadas (con priorización)
- Expectativas realistas de empleabilidad (con timeline)
- Estrategia de seguimiento y evaluación continua

---

CRITERIOS DE CALIDAD OBLIGATORIOS:
- Lenguaje profesional pero accesible
- Análisis basado en evidencia y experiencia clínica
- Recomendaciones prácticas y realizables
- Enfoque positivo y empoderador
- Consideración integral de factores neuroinclusivos
- Propuestas específicas y contextualizadas
- MÍNIMO 2000 palabras de contenido sustancial
- Cada sección debe tener al menos 3-4 párrafos detallados
- Incluir ejemplos concretos y casos de uso
- Proporcionar recursos específicos y accionables
"""

    # Llamada a la API
    respuesta = client.chat.completions.create(
        model=DEPLOYMENT,
        messages=[
            {"role": "system", "content": "Eres un psicólogo laboral experto en neuroinclusión, con más de 15 años de experiencia en orientación profesional para personas neurodivergentes. Tienes formación en psicología clínica, neuropsicología y empleabilidad. Tu enfoque es científico, empático y basado en evidencia. Siempre consideras las fortalezas únicas de cada persona y propones adaptaciones prácticas para maximizar su potencial laboral. IMPORTANTE: Genera informes EXTENSOS y DETALLADOS, no seas escueto."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=8000,
        temperature=0.7
    )

    return respuesta.choices[0].message.content
