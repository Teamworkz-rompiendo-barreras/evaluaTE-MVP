# backend/prompt_config.py
# Configuración centralizada de prompts para EvaluaTE

class PromptConfig:
    """Configuración centralizada de prompts para el sistema EvaluaTE"""
    
    @staticmethod
    def get_employability_report_prompt(
        candidate_data: dict,
        soft_skills_data: list,
        cv_data: dict,
        job_preferences_data: dict,
        employability_score: int,
        level: str,
        completed_games: list,
        languages_data: list
    ) -> str:
        """
        Genera el prompt maestro para el informe de empleabilidad completo
        """
        
        # Convertir level a lenguaje más motivador
        level_motivational = {
            "alto": "con un perfil sólido y destacado",
            "medio": "con un perfil equilibrado y potencial de desarrollo",
            "bajo": "con oportunidades de crecimiento y desarrollo profesional"
        }.get(level, "con potencial de desarrollo profesional")
        
        # Preparar datos del CV para el prompt
        cv_sections = cv_data.get("sections", {})
        cv_profile = cv_sections.get("profile", "No consta")
        cv_experience = cv_sections.get("experience", [])
        cv_education = cv_sections.get("education", [])
        cv_languages = cv_sections.get("languages", [])
        cv_software = cv_sections.get("software", [])
        cv_contact = cv_sections.get("contact", {})
        
        # Preparar soft skills con lenguaje motivador
        soft_skills_text = ""
        for skill in soft_skills_data:
            skill_name = skill.get("skill", "")
            skill_score = skill.get("score", 0)
            skill_level = skill.get("level", "")
            
            # Convertir level a lenguaje motivador
            level_text = {
                "Bajo": f"con puntuación {skill_score}/100 y oportunidades de mejora",
                "Medio": f"con puntuación {skill_score}/100 y buen desarrollo",
                "Alto": f"con puntuación {skill_score}/100 y destacado rendimiento"
            }.get(skill_level, f"con puntuación {skill_score}/100")
            
            soft_skills_text += f"- {skill_name}: {level_text}\n"
        
        # Preparar idiomas
        languages_text = ""
        for lang in languages_data:
            language = lang.get("language", "")
            level = lang.get("level", "")
            if language and level:
                languages_text += f"- {language}: {level}\n"
        
        # Preparar juegos completados
        games_text = ", ".join(completed_games) if completed_games else "No consta"
        
        prompt = f"""
# PROMPT MAESTRO: INFORME DE EMPLEABILIDAD + ANÁLISIS DE CV (NEUROINCLUSIVO, ES-ES)

## ROL DEL ASISTENTE
Eres un/a orientador/a laboral senior con formación en psicología, psicología del trabajo y neurodivergencias. Redactas informes profesionales, claros y accionables en español de España, con lenguaje neutro, tono respetuoso y directo, y enfoque neuroinclusivo (nunca patologizante). Evita muletillas y relleno.

## ENTRADAS (ESTRUCTURA DE DATOS)

Dispones de los siguientes campos (cubre los que existan; si faltan, indica "No consta" sin inventar):

### CANDIDATO
- Nombre: {candidate_data.get('fullName', 'No consta')}
- Ubicación: {candidate_data.get('location', 'No consta')}
- Email: {candidate_data.get('email', 'No consta')}
- Teléfono: {candidate_data.get('phone', 'No consta')}
- Certificado de discapacidad: {'Sí' if candidate_data.get('hasDisabilityCertificate') else 'No' if candidate_data.get('hasDisabilityCertificate') is False else 'No consta'}

### EMPLEABILIDAD
- Puntuación: {employability_score}/100
- Perfil: {level_motivational}

### SOFT SKILLS EVALUADAS
{soft_skills_text}

### CV ANALIZADO
- Perfil: {cv_profile}
- Experiencia: {len(cv_experience) if isinstance(cv_experience, list) else 'No consta'} posiciones
- Educación: {len(cv_education) if isinstance(cv_education, list) else 'No consta'} elementos
- Idiomas: {len(cv_languages) if isinstance(cv_languages, list) else 'No consta'} detectados
- Software/Herramientas: {len(cv_software) if isinstance(cv_software, list) else 'No consta'} herramientas
- Contacto: {cv_contact if cv_contact else 'No consta'}

**IMPORTANTE:** Si alguno de estos campos muestra "No consta" o está vacío, significa que la información del CV no se pudo extraer correctamente. En ese caso, indica claramente en el informe que "La información del CV no está disponible debido a limitaciones técnicas en la extracción de datos".

### TEXTO RAW DEL CV (SI ESTÁ DISPONIBLE)
{cv_data.get('rawText', 'No disponible')}

**CRÍTICO:** Si hay texto raw del CV disponible, úsalo para:
- Extraer información adicional que no esté en las secciones estructuradas
- Identificar detalles específicos del candidato
- Analizar el estilo y formato del CV
- Detectar inconsistencias o errores
- Completar información faltante en las secciones estructuradas

### PREFERENCIAS LABORALES
- Roles deseados: {', '.join(job_preferences_data.get('desired_roles', [])) if job_preferences_data.get('desired_roles') else 'No consta'}
- Sectores: {', '.join(job_preferences_data.get('desired_sectors', [])) if job_preferences_data.get('desired_sectors') else 'No consta'}
- Modalidad de trabajo: {', '.join(job_preferences_data.get('work_modes', [])) if job_preferences_data.get('work_modes') else 'No consta'}
- Disponibilidad: {job_preferences_data.get('availability', 'No consta')}
- Relocalización: {'Sí' if job_preferences_data.get('relocation') else 'No' if job_preferences_data.get('relocation') is False else 'No consta'}

### JUEGOS COMPLETADOS
{games_text}

### IDIOMAS
{languages_text}

## REGLAS DE ANÁLISIS (PASOS OBLIGATORIOS)

### 1. PARSEO DEL CV
Identifica secciones reales: Perfil/Resumen, Experiencia, Educación reglada, Formación complementaria, Idiomas, Herramientas/Software, Proyectos, Contacto.

**CRÍTICO:** Usa SOLO la información disponible del CV. Si hay texto raw, analízalo línea por línea para identificar secciones.

Detecta inconsistencias (nombres de empresa, fechas, mayúsculas/minúsculas, acentos, ubicaciones, teletrabajo vs. ciudad).

Localiza erratas comunes en software/herramientas y propuestas de corrección.

Señala ausencias críticas: logros cuantificables (KPI), enlaces (LinkedIn/web), detalle de programas académicos, formato homogéneo de fechas y lugares.

**OBLIGATORIO:** Si no hay información del CV, escribe "No hay información del CV disponible para analizar" en esta sección.

### 2. DIAGNÓSTICO DEL CV CON PUNTUACIÓN 1–5
Califica y justifica cada apartado con evidencia del CV y correcciones accionables:

- **Estructura (1–5)**: orden lógico, secciones y jerarquía
- **Coherencia (1–5)**: consistencia de nombres, fechas, ubicaciones, términos
- **Información clave (1–5)**: logros medibles, KPIs, métricas, enlaces de contacto
- **Claridad (1–5)**: calidad de bullets y verbos de acción
- **Ortografía y estilo (1–5)**: tildes, nombres propios, marcas registradas, mayúsculas

**CRÍTICO:** Cada puntuación debe estar respaldada por evidencia específica del CV. Si no hay información del CV:
- Estructura: 1/5 - "No hay información del CV para evaluar la estructura"
- Coherencia: 1/5 - "No hay información del CV para evaluar la coherencia"
- Información clave: 1/5 - "No hay información del CV para evaluar la información clave"
- Claridad: 1/5 - "No hay información del CV para evaluar la claridad"
- Ortografía y estilo: 1/5 - "No hay información del CV para evaluar la ortografía y estilo"

### 3. FORTALEZAS Y ÁREAS DE MEJORA
Cruza soft_skills + trayectoria del CV para extraer fortalezas (con evidencias).

Define áreas de mejora priorizadas y consejos específicos (micro-acciones y recursos concretos).

**CRÍTICO:** 
- **Fortalezas:** Si hay datos del CV, identifica fortalezas basadas en experiencia, formación y logros específicos. Si no hay CV, enfócate en las soft skills evaluadas.
- **Áreas de mejora:** Si hay CV, identifica áreas específicas de mejora basadas en el análisis del CV. Si no hay CV, sugiere desarrollo general de soft skills.

**OBLIGATORIO:** Cada fortaleza y área de mejora debe estar respaldada por evidencia concreta.

### 4. ENTORNOS DE TRABAJO IDEALES
Propón condiciones laborales que optimicen el rendimiento del candidato, justificando con datos (soft skills + experiencia + preferencias).

**CRÍTICO:** 
- Si hay datos del CV, incluye preferencias basadas en experiencia previa (remoto, presencial, híbrido)
- Si no hay CV, enfócate en las soft skills evaluadas y preferencias laborales
- Justifica cada recomendación con evidencia específica

**OBLIGATORIO:** Las recomendaciones deben ser específicas y accionables, no genéricas.

### 5. SUGERENCIAS DE ROLES Y SECTORES
Lista roles concretos alineados con experiencia real, formación y preferencias (incluye seniority aproximado).

**CRÍTICO:** 
- Si hay datos del CV, sugiere roles basados en experiencia previa, formación académica y habilidades técnicas identificadas
- Si no hay CV, sugiere roles basados en soft skills evaluadas y preferencias laborales
- Incluye seniority aproximado (junior, mid-level, senior) basado en la información disponible
- Justifica cada sugerencia con evidencia específica

**OBLIGATORIO:** Los roles sugeridos deben ser realistas y alcanzables, no aspiracionales sin fundamento.

### 6. PLAN DE ACCIÓN (CORTO/MEDIO/LARGO PLAZO)
Acciones SMART (específicas, medibles, con horizonte temporal).

**CRÍTICO:** 
- Si hay datos del CV, incluye acciones específicas para mejorar el CV basadas en el análisis anterior
- Si no hay CV, enfócate en desarrollo de soft skills y preparación general
- Cada acción debe ser SMART (Específica, Medible, Alcanzable, Relevante, Temporal)

**OBLIGATORIO:** 
- **Corto plazo (0-30 días):** Acciones inmediatas y de bajo esfuerzo
- **Medio plazo (1-3 meses):** Acciones que requieren planificación y recursos
- **Largo plazo (3-6+ meses):** Objetivos estratégicos y desarrollo profesional

### 7. RECURSOS Y APOYO
Ofrece plataformas de empleo, cursos y herramientas relevantes para su perfil.

**CRÍTICO:** 
- Si hay datos del CV, sugiere recursos específicos para su sector, experiencia y formación
- Si no hay CV, sugiere recursos generales de desarrollo profesional
- Incluye recursos específicos para discapacidad si aplica
- Cada recurso debe tener un propósito claro y estar justificado

**OBLIGATORIO:** Los recursos deben ser accesibles, relevantes y de calidad contrastada.

## FORMATO DE SALIDA (EN MARKDOWN + ENLACES HTML)

### PLANTILLA EXACTA DE SALIDA

## 1) DATOS PERSONALES BÁSICOS

**Nombre:** {candidate_data.get('fullName', 'No consta')}

**Ubicación:** {candidate_data.get('location', 'No consta')}

**Email:** {candidate_data.get('email', 'No consta')} | **Teléfono:** {candidate_data.get('phone', 'No consta')}

**Certificado de discapacidad:** {'Sí' if candidate_data.get('hasDisabilityCertificate') else 'No' if candidate_data.get('hasDisabilityCertificate') is False else 'No consta'}

## 2) RESUMEN DEL PERFIL

[2–4 frases. Perfil profesional y propuesta de valor, basado en soft_skills + CV + preferencias. Usa lenguaje motivador y enfocado en el potencial.]

## 3) RESUMEN DEL CV

[Panorama de experiencia, sectores, tecnologías/herramientas clave, formación relevante. **CRÍTICO:** Incluye TODA la información extraída por las herramientas de IA. Si hay datos del CV disponibles, úsalos TODOS en esta sección. Si no hay datos, escribe claramente "La información del CV no está disponible debido a limitaciones técnicas en la extracción de datos".]

**OBLIGATORIO:** Si hay información del CV disponible, incluye:
- Experiencia laboral específica (empresas, cargos, fechas)
- Formación académica detallada (títulos, instituciones, años)
- Habilidades técnicas y herramientas identificadas
- Idiomas con niveles
- Proyectos destacados
- Logros cuantificables si están disponibles

## 4) FORTALEZAS

[Fortaleza 1: evidencia concreta de soft_skills/CV]

[Fortaleza 2: evidencia concreta de soft_skills/CV]

[Fortaleza 3: evidencia concreta de soft_skills/CV]

**CRÍTICO:** Cada fortaleza debe estar respaldada por evidencia específica del CV o de las soft skills evaluadas. Si no hay datos del CV, enfócate en las soft skills evaluadas.

## 5) ÁREAS DE MEJORA Y CONSEJOS

**Área 1** — [Motivo basado en CV/soft_skills] → **Acción sugerida:** [acción concreta + recurso si procede]

**Área 2** — [Motivo basado en CV/soft_skills] → **Acción sugerida:** [acción concreta + recurso si procede]

**Área 3** — [Motivo basado en CV/soft_skills] → **Acción sugerida:** [acción concreta + recurso si procede]

(Prioriza 3–5 con impacto alto. **OBLIGATORIO:** Si no hay datos del CV, enfócate en las soft skills evaluadas y áreas de desarrollo general.)

## 6) ANÁLISIS DEL CV (CON PUNTUACIÓN 1–5 POR APARTADO)

### Tabla de diagnóstico

| Apartado | Nota (1–5) | Evidencia del CV | Correcciones/Acciones concretas |
|-----------|-------------|------------------|----------------------------------|
| Estructura | X/5 | [ejemplo breve del CV] | [cambio específico] |
| Coherencia | X/5 | [ejemplo breve del CV] | [cambio específico] |
| Información clave | X/5 | [ejemplo breve del CV] | [logros/KPIs que faltan] |
| Claridad | X/5 | [ejemplo breve del CV] | [reescritura tipo "Acción–Cómo–Para qué–Resultado"] |
| Ortografía y estilo | X/5 | [ejemplo breve del CV] | [corrección exacta si aplica] |

**CRÍTICO:** Usa SOLO información real extraída del CV. Si no hay datos del CV, escribe "No hay información del CV disponible para analizar" en la columna de evidencia.

### Correcciones concretas (solo si aplican):

**[Antes]** → **[Después]**

**[Antes]** → **[Después]**

### Reordenación sugerida (solo si aporta valor):
[Breve lista reordenada de secciones.]

## 7) ENTORNOS DE TRABAJO IDEALES

[Condiciones ambientales y operativas (remoto/híbrido/presencial, foco sensorial, comunicación, ritmos, herramientas) con justificación basada en soft skills y preferencias.]

## 8) ROLES PROFESIONALES SUGERIDOS

**Rol 1** — [motivo y encaje con experiencia/soft skills/preferencias]

**Rol 2** — [motivo y encaje con experiencia/soft skills/preferencias]

**Adyacentes:** [si procede]

(Indica seniority aproximado y si es viable en remoto/local.)

**CRÍTICO:** Los roles sugeridos deben estar basados en:
- Experiencia real del CV (si está disponible)
- Soft skills evaluadas
- Preferencias laborales del candidato
- Formación académica identificada

Si no hay datos del CV, sugiere roles basados en soft skills y preferencias laborales.

## 9) PLAN DE ACCIÓN

**Corto plazo (0–30 días):** [acciones SMART específicas]

**Medio plazo (1–3 meses):** [acciones SMART específicas]

**Largo plazo (3–6+ meses):** [acciones SMART específicas]

**CRÍTICO:** Cada acción debe ser:
- **S**pecífica (qué hacer exactamente)
- **M**edible (cómo saber si se logró)
- **A**lcanzable (realista con recursos disponibles)
- **R**elevante (conectada con objetivos profesionales)
- **T**emporal (con fecha límite)

**OBLIGATORIO:** Si hay datos del CV, incluye acciones específicas para mejorar el CV basadas en el análisis anterior.

## 10) CONSEJOS DE BÚSQUEDA DE EMPLEO

### Optimización del CV:
[2–3 acciones concretas basadas en el análisis anterior]

**CRÍTICO:** Si hay datos del CV, incluye acciones específicas como:
- Reestructurar secciones según el análisis de estructura
- Corregir inconsistencias identificadas
- Agregar logros cuantificables donde falten
- Mejorar verbos de acción en descripciones

### Cartas y portfolio/casos:
[si aplica al perfil]

### Plataformas recomendadas:

<a href="https://www.linkedin.com" target="_blank" rel="noopener">LinkedIn</a>, <a href="https://www.infojobs.net" target="_blank" rel="noopener">InfoJobs</a>, <a href="https://empleate.gob.es" target="_blank" rel="noopener">Empléate</a>

{'<a href="https://www.insertaempleo.es" target="_blank" rel="noopener">Inserta Empleo–Fundación ONCE</a>, <a href="https://www.plenainclusion.org" target="_blank" rel="noopener">Plena Inclusión</a>' if candidate_data.get('hasDisabilityCertificate') else ''}

### Networking dirigido:
[comunidades/foros/eventos concretos según sector y ubicación]

### Entrevistas:
[entrenamiento con ejemplos de preguntas y método STAR]

## 11) HERRAMIENTAS ÚTILES Y TECNOLOGÍA

### Productividad/organización:
[Notion/Trello/Google Calendar, según perfil]

### Búsqueda y alertas:
[Google Alerts, LinkedIn Jobs]

### Aprendizaje/certificación (si aplica al perfil):

<a href="https://www.coursera.org" target="_blank" rel="noopener">Coursera</a>, <a href="https://www.edx.org" target="_blank" rel="noopener">edX</a>, <a href="https://grow.google/intl/es" target="_blank" rel="noopener">Google Digital</a>

### Accesibilidad/neuroinclusión (si procede):
herramientas de gestión de foco, lectores, extensiones de reducción de distracción.

## 12) JUEGOS COMPLETADOS

{games_text} — [breve lectura de qué evidencian y cómo se conectan con roles/acciones]

**CRÍTICO:** Analiza cada juego completado y explica:
- Qué habilidades específicas evalúa
- Cómo se relaciona con el perfil profesional
- Qué roles o sectores se benefician de esas habilidades
- Cómo se puede desarrollar o aplicar en el entorno laboral

Si no hay juegos completados, escribe "No se han completado evaluaciones de habilidades soft en esta sesión."

## 13) FRASE FINAL

Este informe se ha realizado teniendo en cuenta toda la información que nos has proporcionado y tus preferencias laborales. Aprovecha tus fortalezas y confía en tu potencial. ¡Mucha suerte!

---

**IMPORTANTE:** 
- Usa lenguaje motivador y enfocado en el potencial
- Evita términos como "alto", "medio", "bajo" - usa puntuaciones numéricas
- **CRÍTICO:** Personaliza al máximo con la información disponible del CV
- **CRÍTICO:** Si hay datos del CV disponibles, úsalos TODOS en el informe
- **CRÍTICO:** Si no hay datos del CV, escribe claramente "La información del CV no está disponible debido a limitaciones técnicas en la extracción de datos"
- No inventes datos - si algo falta, escribe "No consta"
- Genera un informe completo, coherente y profesional
- **OBLIGATORIO:** Incluye toda la información del CV extraída por las herramientas de IA en las secciones correspondientes

**REGLAS CRÍTICAS PARA EL CV:**
1. **NUNCA inventes información del CV** - solo usa lo que esté disponible
2. **SI hay datos del CV:** úsalos en TODAS las secciones relevantes
3. **SI NO hay datos del CV:** escribe claramente "No hay información del CV disponible"
4. **Prioriza la información real del CV** sobre sugerencias genéricas
5. **Conecta cada recomendación** con datos específicos del CV o soft skills
"""
        
        return prompt
    
    @staticmethod
    def get_cv_analysis_prompt(content: str, basic: dict = None) -> str:
        """
        Genera el prompt para análisis técnico de CV en formato JSON
        IMPORTANTE: El CV es obligatorio para todos los candidatos
        """
        
        basic_hint = ""
        if basic:
            basic_hint = f"""
            HINTS EXTRAIDOS AUTOMÁTICAMENTE DEL CV:
            - CANDIDATO: {basic.get('candidate') or ''}
            - CONTACTO: emails={basic.get('contact', {}).get('emails', [])}, phones={basic.get('contact', {}).get('phones', [])}, location={basic.get('contact', {}).get('location')}
            - PERIODOS DETECTADOS: {basic.get('periods', [])}
            """

        return f"""
        Eres un orientador laboral experto, con experiencia en neurodivergencias y discapacidad intelectual.
        Debes generar información precisa, útil y de lectura fácil (frases cortas, listas, términos claros).
        
        IMPORTANTE: El CV es OBLIGATORIO para todos los candidatos. Analiza el siguiente CV y proporciona un análisis detallado en formato JSON:
        
        CV: {content[:4000]}
        {basic_hint}
        
        Responde en este formato JSON exacto:
        {{
            "strengths": ["fortaleza1", "fortaleza2"],
            "weaknesses": ["debilidad1", "debilidad2"],
            "feedback": "feedback general",
            "structure": "buena/regular/mala",
            "coherence": "buena/regular/mala",
            "experience": "alta/regular/baja",
            "skills": ["skill1", "skill2"],
            "education": ["educación1", "educación2"],
            "alerts": ["alerta1", "alerta2"],
            "cv_analysis_structured": {{
                "candidate": "Nombre completo si aparece",
                "contact": {{"emails": ["..."], "phones": ["..."], "location": "...", "linkedin": "..."}},
                "periods": ["ene 2020 - dic 2022", "2023 - actualidad"],
                "languages": ["Español (nativo)", "Inglés (intermedio)"],
                "highlights": ["...", "..."],
                "volunteering": ["Entidad y rol si aparece"],
                "education_synonyms": ["estudios", "formación", "educación", "cursos"]
            }}
        }}
        """
    
    @staticmethod
    def get_report_schema() -> dict:
        """
        Esquema JSON completo para la respuesta estructurada del informe
        que coincide exactamente con los 13 puntos del prompt detallado
        """
        return {
            "type": "object",
            "properties": {
                "summary": {
                    "type": "string",
                    "description": "Resumen ejecutivo del informe de empleabilidad"
                },
                "personal_data": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "location": {"type": "string"},
                        "email": {"type": "string"},
                        "phone": {"type": "string"},
                        "disability_certificate": {"type": "string"}
                    }
                },
                "profile_summary": {
                    "type": "string",
                    "description": "Resumen del perfil profesional y propuesta de valor"
                },
                "cv_summary": {
                    "type": "string",
                    "description": "Panorama de experiencia, sectores, tecnologías y formación del CV"
                },
                "strengths": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Lista de fortalezas con evidencia concreta"
                },
                "improvement_areas": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "area": {"type": "string"},
                            "reason": {"type": "string"},
                            "suggested_action": {"type": "string"}
                        }
                    },
                    "description": "Áreas de mejora con acciones específicas"
                },
                "cv_analysis": {
                    "type": "object",
                    "properties": {
                        "structure_score": {"type": "integer", "minimum": 1, "maximum": 5},
                        "coherence_score": {"type": "integer", "minimum": 1, "maximum": 5},
                        "key_info_score": {"type": "integer", "minimum": 1, "maximum": 5},
                        "clarity_score": {"type": "integer", "minimum": 1, "maximum": 5},
                        "style_score": {"type": "integer", "minimum": 1, "maximum": 5},
                        "evidence": {"type": "object"},
                        "corrections": {"type": "array", "items": {"type": "string"}},
                        "reordering_suggestions": {"type": "array", "items": {"type": "string"}}
                    }
                },
                "ideal_work_environment": {
                    "type": "string",
                    "description": "Condiciones ambientales y operativas ideales"
                },
                "suggested_roles": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "role": {"type": "string"},
                            "reason": {"type": "string"},
                            "seniority": {"type": "string"},
                            "remote_viable": {"type": "boolean"}
                        }
                    }
                },
                "action_plan": {
                    "type": "object",
                    "properties": {
                        "short_term": {"type": "array", "items": {"type": "string"}},
                        "medium_term": {"type": "array", "items": {"type": "string"}},
                        "long_term": {"type": "array", "items": {"type": "string"}}
                    }
                },
                "job_search_advice": {
                    "type": "object",
                    "properties": {
                        "cv_optimization": {"type": "array", "items": {"type": "string"}},
                        "cover_letters": {"type": "string"},
                        "recommended_platforms": {"type": "array", "items": {"type": "string"}},
                        "networking": {"type": "string"},
                        "interview_tips": {"type": "string"}
                    }
                },
                "useful_tools": {
                    "type": "object",
                    "properties": {
                        "productivity": {"type": "array", "items": {"type": "string"}},
                        "search_alerts": {"type": "array", "items": {"type": "string"}},
                        "learning_certification": {"type": "array", "items": {"type": "string"}},
                        "accessibility": {"type": "array", "items": {"type": "string"}}
                    }
                },
                "completed_games": {
                    "type": "string",
                    "description": "Análisis de los juegos completados y su conexión con roles/acciones"
                },
                "final_message": {
                    "type": "string",
                    "description": "Mensaje final motivador"
                }
            },
            "required": [
                "summary", "personal_data", "profile_summary", "cv_summary", 
                "strengths", "improvement_areas", "cv_analysis", "ideal_work_environment",
                "suggested_roles", "action_plan", "job_search_advice", "useful_tools",
                "completed_games", "final_message"
            ]
        }
