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

Detecta inconsistencias (nombres de empresa, fechas, mayúsculas/minúsculas, acentos, ubicaciones, teletrabajo vs. ciudad).

Localiza erratas comunes en software/herramientas y propuestas de corrección.

Señala ausencias críticas: logros cuantificables (KPI), enlaces (LinkedIn/web), detalle de programas académicos, formato homogéneo de fechas y lugares.

### 2. DIAGNÓSTICO DEL CV CON PUNTUACIÓN 1–5
Califica y justifica cada apartado con evidencia del CV y correcciones accionables:

- **Estructura (1–5)**: orden lógico, secciones y jerarquía
- **Coherencia (1–5)**: consistencia de nombres, fechas, ubicaciones, términos
- **Información clave (1–5)**: logros medibles, KPIs, métricas, enlaces de contacto
- **Claridad (1–5)**: calidad de bullets y verbos de acción
- **Ortografía y estilo (1–5)**: tildes, nombres propios, marcas registradas, mayúsculas

### 3. FORTALEZAS Y ÁREAS DE MEJORA
Cruza soft_skills + trayectoria del CV para extraer fortalezas (con evidencias).

Define áreas de mejora priorizadas y consejos específicos (micro-acciones y recursos concretos).

### 4. ENTORNOS DE TRABAJO IDEALES
Propón condiciones laborales que optimicen el rendimiento del candidato, justificando con datos (soft skills + experiencia + preferencias).

### 5. SUGERENCIAS DE ROLES Y SECTORES
Lista roles concretos alineados con experiencia real, formación y preferencias (incluye seniority aproximado).

### 6. PLAN DE ACCIÓN (CORTO/MEDIO/LARGO PLAZO)
Acciones SMART (específicas, medibles, con horizonte temporal).

### 7. RECURSOS Y APOYO
Ofrece plataformas de empleo, cursos y herramientas relevantes para su perfil.

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

[Panorama de experiencia, sectores, tecnologías/herramientas clave, formación relevante. Incluye toda la información extraída por las herramientas de IA.]

## 4) FORTALEZAS

[Fortaleza 1: evidencia concreta de soft_skills/CV]

[Fortaleza 2: evidencia concreta de soft_skills/CV]

[Fortaleza 3: evidencia concreta de soft_skills/CV]

## 5) ÁREAS DE MEJORA Y CONSEJOS

**Área 1** — [Motivo] → **Acción sugerida:** [acción concreta + recurso si procede]

**Área 2** — [Motivo] → **Acción sugerida:** [acción concreta + recurso si procede]

**Área 3** — [Motivo] → **Acción sugerida:** [acción concreta + recurso si procede]

(Prioriza 3–5 con impacto alto.)

## 6) ANÁLISIS DEL CV (CON PUNTUACIÓN 1–5 POR APARTADO)

### Tabla de diagnóstico

| Apartado | Nota (1–5) | Evidencia del CV | Correcciones/Acciones concretas |
|-----------|-------------|------------------|----------------------------------|
| Estructura | X/5 | [ejemplo breve] | [cambio específico] |
| Coherencia | X/5 | [ejemplo breve] | [cambio específico] |
| Información clave | X/5 | [ejemplo breve] | [logros/KPIs que faltan] |
| Claridad | X/5 | [ejemplo breve] | [reescritura tipo "Acción–Cómo–Para qué–Resultado"] |
| Ortografía y estilo | X/5 | [ejemplo breve] | [corrección exacta si aplica] |

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

## 9) PLAN DE ACCIÓN

**Corto plazo (0–30 días):** [acciones SMART específicas]

**Medio plazo (1–3 meses):** [acciones SMART específicas]

**Largo plazo (3–6+ meses):** [acciones SMART específicas]

## 10) CONSEJOS DE BÚSQUEDA DE EMPLEO

### Optimización del CV:
[2–3 acciones concretas basadas en el análisis anterior]

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

## 13) FRASE FINAL

Este informe se ha realizado teniendo en cuenta toda la información que nos has proporcionado y tus preferencias laborales. Aprovecha tus fortalezas y confía en tu potencial. ¡Mucha suerte!

---

**IMPORTANTE:** 
- Usa lenguaje motivador y enfocado en el potencial
- Evita términos como "alto", "medio", "bajo" - usa puntuaciones numéricas
- Personaliza al máximo con la información disponible del CV
- No inventes datos - si algo falta, escribe "No consta"
- Genera un informe completo, coherente y profesional
- Incluye toda la información del CV extraída por las herramientas de IA
"""
        
        return prompt
    
    @staticmethod
    def get_report_schema() -> dict:
        """
        Esquema JSON para la respuesta estructurada del informe
        """
        return {
            "type": "object",
            "properties": {
                "summary": {
                    "type": "string",
                    "description": "Resumen ejecutivo del informe de empleabilidad"
                },
                "recommendations": {
                    "type": "object",
                    "properties": {
                        "cv_analysis": {
                            "type": "object",
                            "properties": {
                                "structure_score": {"type": "integer", "minimum": 1, "maximum": 5},
                                "coherence_score": {"type": "integer", "minimum": 1, "maximum": 5},
                                "content_score": {"type": "integer", "minimum": 1, "maximum": 5},
                                "clarity_score": {"type": "integer", "minimum": 1, "maximum": 5},
                                "style_score": {"type": "integer", "minimum": 1, "maximum": 5},
                                "corrections": {"type": "array", "items": {"type": "string"}},
                                "reordering_suggestions": {"type": "array", "items": {"type": "string"}}
                            }
                        },
                        "strengths": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Lista de fortalezas identificadas"
                        },
                        "improvement_areas": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Áreas de mejora con acciones específicas"
                        },
                        "ideal_work_environment": {
                            "type": "string",
                            "description": "Descripción del entorno de trabajo ideal"
                        },
                        "suggested_roles": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Roles profesionales sugeridos"
                        },
                        "action_plan": {
                            "type": "object",
                            "properties": {
                                "short_term": {"type": "array", "items": {"type": "string"}},
                                "medium_term": {"type": "array", "items": {"type": "string"}},
                                "long_term": {"type": "array", "items": {"type": "string"}}
                            }
                        },
                        "resources": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Recursos y herramientas recomendadas"
                        }
                    }
                }
            },
            "required": ["summary", "recommendations"]
        }
