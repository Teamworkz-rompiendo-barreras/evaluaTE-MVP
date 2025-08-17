# backend/prompt_config.py
# Configuración centralizada de prompts para EvaluaTE

import json
from datetime import datetime

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
            skill_level = (skill.get("level", "") or "").lower()
            
            # Convertir level a lenguaje motivador
            level_text = {
                "bajo": f"con puntuación {skill_score}/100 y oportunidades de mejora",
                "medio": f"con puntuación {skill_score}/100 y buen desarrollo",
                "alto": f"con puntuación {skill_score}/100 y destacado rendimiento"
            }.get(skill_level, f"con puntuación {skill_score}/100")
            
            soft_skills_text += f"- {skill_name}: {level_text}\n"
        
        # Preparar idiomas
        languages_text = ""
        for lang in languages_data:
            language = lang.get("language", "")
            lang_level = lang.get("level", "")
            if language and lang_level:
                languages_text += f"- {language}: {lang_level}\n"
        
        # Preparar juegos completados
        games_text = ", ".join(completed_games) if completed_games else "No consta"
        
        prompt = f"""
# PROMPT MAESTRO: INFORME DE EMPLEABILIDAD + ANÁLISIS DE CV (NEUROINCLUSIVO, ES-ES)

## ROL DEL ASISTENTE
Eres un/a orientador/a laboral senior con formación en psicología, psicología del trabajo y neurodivergencias. Redactas informes profesionales, claros y accionables en español de España, con lenguaje neutro, tono respetuoso y directo, y enfoque neuroinclusivo (nunca patologizante). Evita muletillas y relleno.

## ESTRUCTURA OBLIGATORIA DEL INFORME (13 PUNTOS EXACTOS)

Tu informe DEBE incluir EXACTAMENTE estas 13 secciones en este orden:

1. **DATOS PERSONALES BÁSICOS** - Nombre, ubicación, email, teléfono, certificado de discapacidad
2. **RESUMEN DEL PERFIL** - Perfil profesional y propuesta de valor basado en soft skills + CV + preferencias
3. **RESUMEN DEL CV** - Panorama de experiencia, sectores, tecnologías, formación relevante
4. **FORTALEZAS (CRUZANDO MINIJUEGOS Y CV)** - Fortalezas con evidencia concreta del CV y soft skills
5. **ÁREAS DE MEJORA Y CONSEJOS (PRIORIZADAS Y ACCIONABLES)** - Áreas de mejora con acciones específicas
6. **ANÁLISIS DEL CV CON PUNTUACIÓN 1-5 POR APARTADO** - Estructura, coherencia, información clave, claridad, ortografía/estilo
7. **ENTORNOS DE TRABAJO IDEALES** - Condiciones ambientales y operativas ideales
8. **ROLES PROFESIONALES SUGERIDOS (ALINEADOS CON EXPERIENCIA Y PREFERENCIAS)** - Roles concretos con seniority
9. **PLAN DE ACCIÓN A CORTO, MEDIO Y LARGO PLAZO** - Acciones SMART específicas
10. **CONSEJOS DE BÚSQUEDA DE EMPLEO (CV, NETWORKING, PLATAFORMAS, ENTREVISTAS)** - Estrategias y recursos
11. **HERRAMIENTAS ÚTILES Y TECNOLOGÍA** - Productividad, búsqueda, aprendizaje, accesibilidad
12. **JUEGOS COMPLETADOS (Y QUÉ EVIDENCIAN)** - Análisis de habilidades evaluadas y su aplicación laboral
13. **FRASE FINAL DE CIERRE MOTIVACIONAL Y PERSONALIZADA** - Mensaje final motivador y personalizado

**OBLIGATORIO:** Cada sección debe estar completa y bien desarrollada. No omitas ninguna sección.

**FORMATO DE RESPUESTA:** Debes responder EXCLUSIVAMENTE en formato JSON válido que siga exactamente el esquema proporcionado. NO uses markdown ni texto libre.

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

## CLAVES DE SALIDA (JSON ESTRICTO – DEBE CUMPLIR EL ESQUEMA)
Devuelve ÚNICAMENTE un JSON con estas claves y tipos:

- summary: string
- personal_data: objeto con campos (name:string, location:string, email:string, phone:string, disability_certificate:string)
- profile_summary: string
- cv_summary: string
- strengths: array[string]
- improvement_areas: array de objetos (area:string, reason:string, suggested_action:string)
- cv_analysis: objeto con campos:
  - structure_score:int(1..5), coherence_score:int(1..5), key_info_score:int(1..5), clarity_score:int(1..5), style_score:int(1..5)
  - evidence: objeto con (structure:string, coherence:string, key_info:string, clarity:string, style:string)
  - corrections: array[string], reordering_suggestions: array[string]
- ideal_work_environment: string
- suggested_roles: array de objetos (role:string, reason:string, seniority:string, remote_viable:boolean)
- action_plan: objeto con (short_term: array[string], medium_term: array[string], long_term: array[string])
- job_search_advice: objeto con (cv_optimization: array[string], letters_portfolio:string opcional, recommended_platforms: array[string], networking:string opcional, interview_tips:string opcional)
- useful_tools: objeto con (productivity: array[string], job_search: array[string], learning: array[string], accessibility: array[string])
- completed_games: array[string]
- final_message: string

REGLAS:
- Si falta un dato, escribe "No consta" (no uses null).
- Usa SIEMPRE puntuaciones 1–5 enteras.
- No inventes datos del CV; si no hay CV, indícalo de forma explícita donde corresponda.
- Responde SOLO con el JSON; nada de texto adicional ni Markdown.


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
    def get_system_prompt() -> str:
        """
        Retorna el prompt del sistema para el rol del asistente
        """
        return "Eres un/a orientador/a laboral senior con formación en psicología, psicología del trabajo y neurodivergencias. Redactas informes profesionales, claros y accionables en español de España, con lenguaje neutro, tono respetuoso y directo, y enfoque neuroinclusivo (nunca patologizante)."

    @staticmethod
    def get_report_schema() -> dict:
        """
        JSON Schema que el modelo debe cumplir (13 apartados).
        Devuelve SOLO el schema (el wrapper name/strict se añade en la llamada).
        """
        return {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "summary": {"type": "string"},
                "personal_data": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "name": {"type": "string"},
                        "location": {"type": "string"},
                        "email": {"type": "string"},
                        "phone": {"type": "string"},
                        "disability_certificate": {"type": "string"}
                    }
                },
                "profile_summary": {"type": "string"},
                "cv_summary": {"type": "string"},
                "strengths": {"type": "array", "items": {"type": "string"}},
                "improvement_areas": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "additionalProperties": False,
                        "properties": {
                            "area": {"type": "string"},
                            "reason": {"type": "string"},
                            "suggested_action": {"type": "string"}
                        },
                        "required": ["area", "reason", "suggested_action"]
                    }
                },
                "cv_analysis": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "structure_score": {"type": "integer", "minimum": 1, "maximum": 5},
                        "coherence_score": {"type": "integer", "minimum": 1, "maximum": 5},
                        "key_info_score": {"type": "integer", "minimum": 1, "maximum": 5},
                        "clarity_score": {"type": "integer", "minimum": 1, "maximum": 5},
                        "style_score": {"type": "integer", "minimum": 1, "maximum": 5},
                        "evidence": {
                            "type": "object",
                            "additionalProperties": False,
                            "properties": {
                                "structure": {"type": "string"},
                                "coherence": {"type": "string"},
                                "key_info": {"type": "string"},
                                "clarity": {"type": "string"},
                                "style": {"type": "string"}
                            }
                        },
                        "corrections": {"type": "array", "items": {"type": "string"}},
                        "reordering_suggestions": {"type": "array", "items": {"type": "string"}}
                    }
                },
                "ideal_work_environment": {"type": "string"},
                "suggested_roles": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "additionalProperties": False,
                        "properties": {
                            "role": {"type": "string"},
                            "reason": {"type": "string"},
                            "seniority": {"type": "string"},
                            "remote_viable": {"type": "boolean"}
                        },
                        "required": ["role", "reason"]
                    }
                },
                "action_plan": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "short_term": {"type": "array", "items": {"type": "string"}},
                        "medium_term": {"type": "array", "items": {"type": "string"}},
                        "long_term": {"type": "array", "items": {"type": "string"}}
                    }
                },
                "job_search_advice": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "cv_optimization": {"type": "array", "items": {"type": "string"}},
                        "letters_portfolio": {"type": "string"},
                        "recommended_platforms": {"type": "array", "items": {"type": "string"}},
                        "networking": {"type": "string"},
                        "interview_tips": {"type": "string"}
                    }
                },
                "useful_tools": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "productivity": {"type": "array", "items": {"type": "string"}},
                        "job_search": {"type": "array", "items": {"type": "string"}},
                        "learning": {"type": "array", "items": {"type": "string"}},
                        "accessibility": {"type": "array", "items": {"type": "string"}}
                    }
                },
                "completed_games": {"type": "array", "items": {"type": "string"}},
                "final_message": {"type": "string"}
            },
            "required": [
                "summary", "personal_data", "profile_summary", "cv_summary",
                "strengths", "improvement_areas", "cv_analysis", "ideal_work_environment",
                "suggested_roles", "action_plan", "job_search_advice", "useful_tools",
                "completed_games", "final_message"
            ]
        }
    
    @staticmethod
    def convert_json_to_markdown_report(json_data: dict) -> str:
        """
        Convierte la respuesta JSON a markdown legible (no afecta al JSON que guardas).
        """
        try:
            p = json_data.get('personal_data', {}) or {}
            a = json_data.get('action_plan', {}) or {}
            adv = json_data.get('job_search_advice', {}) or {}
            tools = json_data.get('useful_tools', {}) or {}
            cvx = json_data.get('cv_analysis', {}) or {}

            def stars(n: int) -> str:
                try:
                    n = int(n or 0)
                except:
                    n = 0
                n = max(0, min(5, n))
                return "★"*n + "☆"*(5-n)

            report = f"""# 📋 Informe de Empleabilidad Profesional

## RESUMEN EJECUTIVO
{json_data.get('summary', 'No disponible')}

## 1. DATOS PERSONALES BÁSICOS
- **Nombre**: {p.get('name', 'No consta')}
- **Ubicación**: {p.get('location', 'No consta')}
- **Email**: {p.get('email', 'No consta')}
- **Teléfono**: {p.get('phone', 'No consta')}
- **Certificado de discapacidad**: {p.get('disability_certificate', 'No consta')}

## 2. RESUMEN DEL PERFIL
{json_data.get('profile_summary', 'No disponible')}

## 3. RESUMEN DEL CV
{json_data.get('cv_summary', 'No disponible')}

## 4. FORTALEZAS (CRUZANDO MINIJUEGOS Y CV)
"""
            for s in json_data.get('strengths', []) or []:
                report += f"- {s}\n"

            report += "\n## 5. ÁREAS DE MEJORA Y CONSEJOS (PRIORIZADAS Y ACCIONABLES)\n"
            for it in json_data.get('improvement_areas', []) or []:
                report += f"**{it.get('area','Área')}** — {it.get('reason','')} → **Acción sugerida:** {it.get('suggested_action','')}\n\n"

            report += "## 6. ANÁLISIS DEL CV CON PUNTUACIÓN 1–5 POR APARTADO\n"
            report += f"""
**Estructura:** {stars(cvx.get('structure_score'))} ({cvx.get('structure_score','0')}/5)
**Coherencia:** {stars(cvx.get('coherence_score'))} ({cvx.get('coherence_score','0')}/5)
**Información clave:** {stars(cvx.get('key_info_score'))} ({cvx.get('key_info_score','0')}/5)
**Claridad:** {stars(cvx.get('clarity_score'))} ({cvx.get('clarity_score','0')}/5)
**Ortografía y estilo:** {stars(cvx.get('style_score'))} ({cvx.get('style_score','0')}/5)
"""
            ev = cvx.get('evidence') or {}
            if any(ev.values()):
                report += "\n**Evidencias breves:**\n"
                for k in ("structure","coherence","key_info","clarity","style"):
                    if ev.get(k):
                        report += f"- {k.capitalize()}: {ev.get(k)}\n"

            if cvx.get('corrections'):
                report += "\n**Correcciones concretas:**\n"
                for c in cvx['corrections']:
                    report += f"- {c}\n"

            if cvx.get('reordering_suggestions'):
                report += "\n**Reordenación sugerida:**\n"
                for r in cvx['reordering_suggestions']:
                    report += f"- {r}\n"

            report += f"""

## 7. ENTORNOS DE TRABAJO IDEALES
{json_data.get('ideal_work_environment', 'No disponible')}

## 8. ROLES PROFESIONALES SUGERIDOS (ALINEADOS CON EXPERIENCIA Y PREFERENCIAS)
"""
            for role in json_data.get('suggested_roles', []) or []:
                remoto = "Sí" if role.get('remote_viable') else "No"
                report += f"**{role.get('role','Rol')}** — {role.get('reason','')} (Seniority: {role.get('seniority','No especificado')}, Remoto: {remoto})\n\n"

            report += "## 9. PLAN DE ACCIÓN A CORTO, MEDIO Y LARGO PLAZO\n"
            if a.get('short_term'):
                report += "**Corto plazo (0–30 días):**\n" + "\n".join(f"- {x}" for x in a['short_term']) + "\n\n"
            if a.get('medium_term'):
                report += "**Medio plazo (1–3 meses):**\n" + "\n".join(f"- {x}" for x in a['medium_term']) + "\n\n"
            if a.get('long_term'):
                report += "**Largo plazo (3–6+ meses):**\n" + "\n".join(f"- {x}" for x in a['long_term']) + "\n\n"

            report += "## 10. CONSEJOS DE BÚSQUEDA DE EMPLEO (CV, NETWORKING, PLATAFORMAS, ENTREVISTAS)\n"
            if adv.get('cv_optimization'):
                report += "**Optimización del CV:**\n" + "\n".join(f"- {x}" for x in adv['cv_optimization']) + "\n\n"
            if adv.get('recommended_platforms'):
                report += "**Plataformas recomendadas:**\n" + "\n".join(f"- {x}" for x in adv['recommended_platforms']) + "\n\n"
            if adv.get('letters_portfolio'):
                report += f"**Cartas y portfolio/casos:**\n- {adv['letters_portfolio']}\n\n"
            if adv.get('networking'):
                report += f"**Networking dirigido:**\n- {adv['networking']}\n\n"
            if adv.get('interview_tips'):
                report += f"**Entrevistas:**\n- {adv['interview_tips']}\n\n"

            report += "## 11. HERRAMIENTAS ÚTILES Y TECNOLOGÍA\n"
            def _tools_block(title, arr):
                nonlocal report
                if arr:
                    report += f"**{title}:**\n" + "\n".join(f"- {x}" for x in arr) + "\n\n"
            _tools_block("Productividad/organización", tools.get("productivity"))
            _tools_block("Búsqueda de empleo y alertas", tools.get("job_search"))
            _tools_block("Aprendizaje/certificación", tools.get("learning"))
            _tools_block("Accesibilidad/neuroinclusión", tools.get("accessibility"))

            report += "## 12. JUEGOS COMPLETADOS (Y QUÉ EVIDENCIAN)\n"
            games = json_data.get('completed_games') or []
            if isinstance(games, list) and games:
                report += "\n".join(f"- {g}" for g in games) + "\n"
            else:
                report += (games if isinstance(games, str) else "No disponible") + "\n"

            report += f"""
## 13) FRASE FINAL DE CIERRE MOTIVACIONAL Y PERSONALIZADA
{json_data.get('final_message', 'No disponible')}

---

**Fecha de generación:** {datetime.now().strftime('%d/%m/%Y a las %H:%M')}
"""
            return report
        except Exception as e:
            return f"Error convirtiendo respuesta JSON a markdown: {str(e)}\n\nRespuesta original:\n{json.dumps(json_data, indent=2, ensure_ascii=False)}"
