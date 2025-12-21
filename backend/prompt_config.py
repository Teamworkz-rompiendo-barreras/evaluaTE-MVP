# backend/prompt_config.py
# Configuración centralizada de prompts para EvaluaTE

import json
from datetime import datetime
from typing import Any, Dict, List

class PromptConfig:
    """Configuración centralizada de prompts para el sistema EvaluaTE."""

    @staticmethod
    def make_cv_analysis_block(cv_ui_diag: Dict[str, Any], cv_data: Dict[str, Any]) -> str:
        """Bloque que fija las puntuaciones 1–5 y aporta contexto al modelo sin que las re-calcule."""
        diag = cv_ui_diag or {}
        ev = diag.get("evidence") or {}

        def _g(k, d="—"):
            return str(diag.get(k, d))

        def _e(k):
            return (ev.get(k) or "—").strip()

        lines = [
            "### DIAGNÓSTICO DETERMINISTA DEL CV (NO MODIFICAR PUNTUACIONES, SOLO EXPLICAR Y COMPLEMENTAR)",
            f"- Estructura: {_g('structure_score')}/5 | Evidencia: {_e('structure')}",
            f"- Coherencia: {_g('coherence_score')}/5 | Evidencia: {_e('coherence')}",
            f"- Información clave: {_g('key_info_score')}/5 | Evidencia: {_e('key_info')}",
            f"- Claridad: {_g('clarity_score')}/5 | Evidencia: {_e('clarity')}",
            f"- Ortografía y estilo: {_g('style_score')}/5 | Evidencia: {_e('style')}",
        ]

        corr = [f"- {c}" for c in (diag.get("corrections") or [])]
        if corr:
            lines.append("Correcciones detectadas:")
            lines.extend(corr)
        return "\n".join(lines)

    @staticmethod
    def get_employability_report_prompt(
        candidate_data: dict,
        soft_skills_data: list,
        cv_data: dict,
        job_preferences_data: dict,
        employability_score: int,
        level: str,
        completed_games: list,
        languages_data: list,
        analysis_block: str = ""
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
        
        # Si se proporcionó analysis_json en cv_data, añadir reglas estrictas
        
        # CRÍTICO: Bloque de análisis del CV con estrellas deterministas
        analysis_block = analysis_block or ""
        if not analysis_block and cv_data.get("diagnostico_cv"):
            diag = cv_data["diagnostico_cv"]
            ev = (diag.get("evidence") or {})
            analysis_block = f"""
### DIAGNÓSTICO DEL CV (ANALIZADOR DETERMINISTA)
- Formato: {diag.get('structure_score','No')}/5
- Claridad: {diag.get('clarity_score','No')}/5
- Coherencia: {diag.get('coherence_score','No')}/5
- Información clave: {diag.get('key_info_score','No')}/5
- Ortografía: {diag.get('spelling_style_score','No')}/5
Evidencia breve: {ev.get('structure','')}
"""
        analysis_json = cv_data.get('analysis_json') if isinstance(cv_data, dict) else None
        instr_block = ""
        analysis_json_block = ""
        if analysis_json:
            instr_block = (
                "## INSTRUCCIONES (OBLIGATORIAS)\n"
                "- Usa las puntuaciones del objeto analysis_json tal cual; NO las cambies ni inventes.\n"
                "- Si falta un dato del CV, escribe “no consta”, nunca “CV no disponible”.\n"
                "- Debes citar en el texto los números tal como vienen (1–5) y mantener coherencia en todo el informe.\n"
            )
            analysis_json_block = (
                "### ANALYSIS_JSON (INMUTABLE)\n"
                + json.dumps(analysis_json, ensure_ascii=False)
                + "\n"
            )

        prompt = f"""
# PROMPT MAESTRO: INFORME DE EMPLEABILIDAD + ANÁLISIS DE CV (NEUROINCLUSIVO, ES-ES)

## ROL DEL ASISTENTE
Eres un/a orientador/a laboral senior con formación en psicología, psicología del trabajo y neurodivergencias. Redactas informes profesionales, claros y accionables en español de España, con lenguaje neutro, tono respetuoso y directo, y enfoque neuroinclusivo (nunca patologizante). Evita muletillas y relleno.

## ESTRUCTURA OBLIGATORIA DEL INFORME (13 PUNTOS EXACTOS → CAMPOS JSON)

Tu respuesta debe ser UN objeto JSON con estas 13 claves, en este orden:
1. `personal_data` (nombre, ubicación, email, teléfono, discapacidad)
2. `profile_summary` (3–5 líneas, orientado a valor y preferencias)
3. `cv_analysis_summary` (panorama de experiencia, sectores, tecnologías, formación)
4. `strengths` (lista; cruza minijuegos y CV, evidencia concreta)
5. `improvement_areas` (lista con `area`, `reason`, `suggested_action`)
6. `cv_analysis` (puntuaciones 1–5 + `evidence`, `corrections`, `reordering_suggestions`)
7. `ideal_work_environment` (texto operativo e inclusivo)
8. `suggested_roles` (lista de objetos: `role`, `reason`, `seniority`, `remote_viable`)
9. `action_plan` (tres listas: `short_term`, `medium_term`, `long_term`)
10. `job_search_advice` (tres listas: `cv_optimization`, `letters_portfolio`, `networking`, más `recommended_platforms`, `interview_tips`)
11. `useful_tools` (listas: `productivity`, `job_search`, `learning`, `accessibility`)
12. `completed_games` (lista describiendo juego + cómo capitalizarlo)
13. `final_message` (cierre motivacional personalizado)

cv_details debe existir como objeto con 4 listas (experience, education, languages, tools), cada elemento con campos: title, subtitle, period, level, detail (rellena los que tengas, no inventes).

**OBLIGATORIO:** Cada campo debe estar completo; si falta dato, usa “No consta”. No omitas ningún campo.

**FORMATO DE RESPUESTA:** EXCLUSIVAMENTE JSON válido que siga esta estructura (strict). NO uses markdown ni texto libre.

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
{cv_data.get('rawText', 'No disponible')[:4000]}

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

{instr_block}
{analysis_json_block}
{analysis_block}

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
### REGLA CRÍTICA SOBRE EL CV
- Si existen secciones estructuradas del CV (experience/education/languages/skills/contact), está PROHIBIDO afirmar “no hay información del CV”. Debes puntuar 1–5 usando esas secciones como evidencia.
- Solo puedes escribir “No hay información del CV disponible para analizar” si NO hay texto raw NI secciones estructuradas.

### FORMATO REQUERIDO DE CONTENIDO (ESTILO DEL INFORME)
- Resumen ejecutivo: 3–5 líneas. Cita explícitamente fortalezas principales con sus valores en formato (N/100), preferencias laborales y áreas a potenciar.
- Fortalezas clave: lista; cada ítem como "Nombre (N/100): explicación breve ligada al rol" usando las soft skills con mejor puntuación.
- Áreas de mejora: lista priorizada; cada ítem como "Nombre (N/100): diagnóstico. Acción: micro-acción concreta".
- Diagnóstico del CV (mejoras rápidas): usa las correcciones/evidencias del bloque de diagnóstico determinista y añade sugerencias prácticas (ortografía de marcas, KPIs, ATS, orden de secciones, LinkedIn).
- Entornos de trabajo ideales: bullets operativos (tareas, métricas, modalidad, comunicación, cultura).
- Roles sugeridos: cada elemento incluye "Rol — Seniority — Remoto?" y una "Razón:" breve.
- Plan de acción: 3 listas (0–30, 31–60, 61–90 días) con 4–6 bullets accionables por bloque.
- Consejos prácticos de búsqueda: incluye frases listas (titular, acerca de, mensaje corto) dentro de una subsección textual.
- Juegos completados: lista formateada como "Nombre: cómo capitalizarlo".


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
- cv_details: objeto con (experience: array[string], education: array[string], languages: array[string], tools: array[string])
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
        return (
            "Eres un/a orientador/a laboral senior con formación en psicología del trabajo y neurodivergencias. "
            "Escribes en español de España, tono profesional, claro, directo y neuroinclusivo. "
            "Tu salida debe respetar estrictamente el esquema JSON proporcionado (strict)."
        )

    @staticmethod
    def get_report_schema() -> dict:
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
                    },
                    "required": ["name", "location", "email", "phone", "disability_certificate"]
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
                            },
                            "required": ["structure", "coherence", "key_info", "clarity", "style"]
                        },
                        "corrections": {"type": "array", "items": {"type": "string"}},
                        "reordering_suggestions": {"type": "array", "items": {"type": "string"}}
                    },
                    "required": [
                        "structure_score","coherence_score","key_info_score",
                        "clarity_score","style_score","evidence","corrections","reordering_suggestions"
                    ]
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
                        "required": ["role", "reason", "seniority", "remote_viable"]
                        }
                },
                "action_plan": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "short_term": {"type": "array", "items": {"type": "string"}},
                        "medium_term": {"type": "array", "items": {"type": "string"}},
                        "long_term": {"type": "array", "items": {"type": "string"}}
                    },
                    "required": ["short_term","medium_term","long_term"]
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
                    },
                    "required": [
                        "cv_optimization","letters_portfolio","recommended_platforms","networking","interview_tips"
                    ]
                },
                "useful_tools": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "productivity": {"type": "array", "items": {"type": "string"}},
                        "job_search": {"type": "array", "items": {"type": "string"}},
                        "learning": {"type": "array", "items": {"type": "string"}},
                        "accessibility": {"type": "array", "items": {"type": "string"}}
                    },
                    "required": ["productivity","job_search","learning","accessibility"]
                },
                "completed_games": {"type": "array", "items": {"type": "string"}},
                "final_message": {"type": "string"}
            },
            "required": [
                "summary","personal_data","profile_summary","cv_summary",
                "strengths","improvement_areas","cv_analysis","ideal_work_environment",
                "suggested_roles","action_plan","job_search_advice","useful_tools",
                "completed_games","final_message"
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
