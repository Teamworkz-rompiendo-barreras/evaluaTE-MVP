# backend/generate_report.py

"""
Módulo de generación de informes de empleabilidad

IMPORTANTE: Este módulo NO contiene prompts hardcodeados. Todos los prompts están centralizados
en prompt_config.py para evitar duplicación y facilitar el mantenimiento.

- generar_informe_prueba(): Genera informe de prueba usando el prompt centralizado
- generar_informe(): Genera informe completo usando Azure OpenAI con prompt centralizado
- cargar_feedback_previo(): Carga feedback previo de usuarios

Todos los prompts se obtienen de PromptConfig.get_employability_report_prompt()
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple
from dotenv import load_dotenv

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cargar variables de entorno
load_dotenv()

# Variables de Azure OpenAI
API_KEY = os.getenv('AZURE_OPENAI_API_KEY')
ENDPOINT = os.getenv('AZURE_OPENAI_ENDPOINT')
DEPLOYMENT = os.getenv('AZURE_OPENAI_DEPLOYMENT')
API_VERSION = os.getenv('AZURE_OPENAI_API_VERSION', '2024-10-21')

# Verificar si Azure OpenAI está configurado
AZURE_OPENAI_CONFIGURED = all([API_KEY, ENDPOINT, DEPLOYMENT])

if AZURE_OPENAI_CONFIGURED:
    try:
        from openai import AzureOpenAI
        print("✅ Azure OpenAI configurado correctamente")
    except ImportError:
        print("❌ Error: No se pudo importar Azure OpenAI")
        AZURE_OPENAI_CONFIGURED = False
else:
    print("⚠️ Azure OpenAI no configurado - usando modo de prueba")
    print("Para configurar Azure OpenAI:")
    print("1. Ve a https://portal.azure.com")
    print("2. Crea un recurso 'Azure OpenAI'")
    print("3. Copia la API Key y Endpoint")
    print("4. Crea un deployment con un modelo (gpt-35-turbo, gpt-4, etc.)")
    print("5. Configura las variables en el archivo .env")
def _stars(n: int) -> str:
    try:
        v = int(n)
    except Exception:
        v = 0
    v = max(1, min(5, v))
    return "★" * v + "☆" * (5 - v)

def _take(lst: List[Any], n: int) -> List[Any]:
    return lst[:n] if isinstance(lst, list) else []

def _clamp_pct(v: Any) -> int:
    try:
        n = int(v)
    except Exception:
        n = 0
    return max(0, min(100, n))

def render_real_report_markdown(
    candidate_data: Dict[str, Any],
    soft_skills_data: List[Dict[str, Any]],
    cv_data: Dict[str, Any],
    job_preferences_data: Dict[str, Any],
    languages_data: List[Dict[str, Any]],
    cv_ui_diag: Optional[Dict[str, Any]] = None,
) -> str:
    sections = (cv_data or {}).get("sections", {})
    profile = sections.get("profile") or ""
    exp = sections.get("experience") or []
    edu = sections.get("education") or []
    langs = sections.get("languages") or []
    software = sections.get("software") or sections.get("skills") or []
    contact = sections.get("contact") or {}

    # Top/bottom skills por puntuación real
    sk_sorted = sorted(
        [
            {"name": s.get("skill"), "score": _clamp_pct(s.get("score", 0))}
            for s in (soft_skills_data or [])
            if isinstance(s, dict) and s.get("skill") is not None
        ],
        key=lambda x: x["score"],
        reverse=True,
    )
    top = _take(sk_sorted, 4)
    bottom = _take(list(reversed(sk_sorted)), 2)

    def _fmt_exp_item(e: Dict[str, Any]) -> str:
        role = str(e.get("position") or e.get("title") or "").strip()
        company = str(e.get("company") or e.get("organization") or e.get("organisation") or "").strip()
        start = (e.get("start_date") or "").strip()
        end = ("actual" if e.get("current") else (e.get("end_date") or "").strip())
        when = f" ({start} – {end})" if (start or end) else ""
        at = f", {company}" if company else ""
        return f"{role}{at}{when}" if (role or company or when) else ""

    exp_lines = [x for x in (_fmt_exp_item(e) for e in _take(exp, 3)) if x]
    edu_lines = [
        f"{str(x.get('degree') or x.get('title') or 'Estudios')}{' (' + str(x.get('start_date')) + ' – ' + str(x.get('end_date')) + ')' if x.get('start_date') or x.get('end_date') else ''} — {str(x.get('institution') or x.get('school') or '')}"
        for x in _take(edu, 3)
    ]
    langs_lines = [f"{str(x.get('language') or x.get('name') or 'Idioma')}: {str(x.get('level') or 'No especificado')}" for x in _take(langs, 3)]
    soft_list = [str(s if isinstance(s, str) else (s.get('name') or s.get('tool') or '')) for s in _take(software, 5)]

    # Diagnóstico de CV
    diag = cv_ui_diag or (cv_data or {}).get("cv_diagnostico_ui") or {}
    ds = {
        "Estructura": diag.get("structure_score"),
        "Claridad": diag.get("clarity_score"),
        "Coherencia": diag.get("coherence_score"),
        "Información clave": diag.get("key_info_score"),
        "Ortografía": diag.get("style_score") or diag.get("spelling_style_score"),
    }
    evid = (diag.get("evidence") or {}) if isinstance(diag, dict) else {}
    corrs = diag.get("corrections") or []
    reord = diag.get("reordering_suggestions") or []

    # Datos personales
    name = candidate_data.get("fullName") or "Usuario"
    location = candidate_data.get("location") or contact.get("location") or "No consta"
    email = candidate_data.get("email") or (contact.get("emails") or ["No consta"])[0]
    phone = candidate_data.get("phone") or (contact.get("phones") or ["No especificado"])[0]
    linkedin = (contact.get("linkedin") or "No especificado").strip()

    # Resumen ejecutivo (basado en datos reales)
    top_names = ", ".join([f"{t['name']} ({t['score']}/100)" for t in _take(top, 4)])
    areas_txt = ", ".join([f"{b['name']}" for b in _take(bottom, 2)])
    work_modes = ", ".join(job_preferences_data.get("work_modes", []) or []) or "No especificado"
    availability = job_preferences_data.get("availability", "No especificado")
    relocation = job_preferences_data.get("relocation")
    relocation_txt = "apertura a relocalización" if relocation else ("sin relocalización" if relocation is False else "relocalización no especificada")

    lines = []
    lines.append("## Resumen ejecutivo")
    lines.append("")
    lines.append(
        f"Perfil con {('alta orientación a ' + top[0]['name'].lower() + f' ({top[0]['score']}/100)') if top else 'base de soft skills evaluadas'}"
        + (f" y base en {', '.join([f"{t['name'].lower()} ({t['score']}/100)" for t in _take(top[1:], 3)])}" if len(top) > 1 else "")
        + f". Preferencia por trabajo {work_modes.lower()}, disponibilidad {availability} y {relocation_txt}."
    )
    if exp_lines:
        lines.append(
            " "
            + " ".join(
                [
                    "Experiencia reciente en " + exp_lines[0].split(",")[0].lower() + ".",
                ]
            )
        )
    if areas_txt:
        lines.append(f" Áreas a potenciar: {areas_txt}.")

    # Datos personales
    lines.append("")
    lines.append("## Datos personales")
    lines.append("")
    lines.append(f"Nombre: {name}")
    lines.append("")
    lines.append(f"Ubicación: {location}")
    lines.append("")
    lines.append(f"Email: {email}")
    lines.append("")
    lines.append(f"Teléfono: {phone}")
    lines.append("")
    lines.append(f"LinkedIn: {linkedin or '(no especificado; recomendado crear/actualizar)'}")

    # Resumen de perfil (determinista)
    lines.append("")
    lines.append("## Resumen de perfil")
    prof_txt = "Profesional orientada a la precisión y la organización" if any(soft_list) else "Profesional con experiencia en tareas administrativas"
    domain_txt = "captura y limpieza de datos, transcripción y gestión de información" if any(soft_list) else "gestión de información"
    lines.append("")
    lines.append(
        f"{prof_txt}, con experiencia en {domain_txt}. "
        + ("Ha liderado iniciativas/organizaciones (p. ej., Teamworkz) " if any("Teamwork" in (str(x).title()) for x in soft_list + exp_lines) else "")
        + "demostrando autonomía y responsabilidad. "
        + "Busca consolidarse en operaciones de datos y administración remota, aplicando Microsoft Office y herramientas digitales."
    )

    # Resumen del CV
    lines.append("")
    lines.append("## Resumen del CV")
    lines.append("")
    if exp_lines:
        lines.append("Experiencia (selección)")
        for e in exp_lines:
            lines.append(f"- {e}")
        lines.append("")
    if edu_lines:
        lines.append("Formación (selección)")
        for e in edu_lines:
            lines.append(f"- {e}")
        lines.append("")
    if langs_lines:
        lines.append("Idiomas: " + ", ".join(langs_lines))
    if soft_list:
        lines.append("")
        lines.append("Software: " + ", ".join(soft_list))

    # Fortalezas y áreas
    lines.append("")
    lines.append("## Fortalezas clave")
    for t in top:
        lines.append(f"- {t['name']} ({t['score']}/100): desempeño basado en evaluación y experiencia.")

    lines.append("")
    lines.append("## Áreas de mejora priorizadas")
    for b in bottom:
        lines.append(f"- {b['name']} ({b['score']}/100): acción: práctica guiada y evidencias de impacto.")

    # Diagnóstico CV
    lines.append("")
    lines.append("## Diagnóstico del CV (mejoras rápidas)")
    for label, val in ds.items():
        if val is not None:
            lines.append(f"{label}:\n{_stars(int(val))}")
    # Evidencias/correcciones
    for k in ("structure", "clarity", "coherence", "key_info", "style"):
        txt = str(evid.get(k) or "").strip()
        if txt:
            lines.append(txt)
    if corrs:
        lines.append("")
        lines.append("Correcciones/Acciones:")
        for c in _take(corrs, 5):
            lines.append(f"- {c}")
    if reord:
        lines.append("")
        lines.append("Reordenación sugerida:")
        for r in _take(reord, 3):
            lines.append(f"- {r}")

    # Entornos de trabajo ideales (derivados de preferencias)
    lines.append("")
    lines.append("## Entornos de trabajo ideales")
    wm = ", ".join(job_preferences_data.get("work_modes", []) or []) or "remoto"
    lines.append(f"- Tareas estructuradas y métricas claras. Modalidad: {wm}.")
    lines.append("- Comunicación escrita y procedimientos/checklists.")

    # Roles sugeridos deterministas
    lines.append("")
    lines.append("## Roles sugeridos")
    lines.append("- Grabadora de datos / Data Entry — Junior–Mid — 100% remoto.\n  Razón: experiencia en captura/transcripción y herramientas de oficina.")
    lines.append("- Asistente administrativo remoto / Back-office — Junior–Mid — Remoto viable.\n  Razón: organización y gestión documental.")
    lines.append("- Data Labeling/Annotation — Junior — Remoto.\n  Razón: atención al detalle aplicable a IA/ML.")
    lines.append("- Data QA — Junior — Remoto.\n  Razón: pensamiento analítico para validar y corregir registros.")

    # Plan 30-60-90
    lines.append("")
    lines.append("## Plan de acción (30–60–90 días)")
    lines.append("")
    lines.append("0–30 días (bases)")
    lines.append("- Reescribir CV con logros y métricas; corregir tipografías; crear LinkedIn.")
    lines.append("- Portafolio ligero: 3 ejemplos (Excel limpieza, transcripción, checklist QA).")
    lines.append("- Acreditar velocidad/precisión de tecleo e inglés funcional.")
    lines.append("")
    lines.append("31–60 días (tracción)")
    lines.append("- 10–15 candidaturas/semana a data entry/QA/annotation; 3 mensajes a reclutadores.")
    lines.append("- Aprender OCR básico y herramientas de bases de datos (Airtable/Notion).")
    lines.append("- SOPs personales: plantillas y control de versiones.")
    lines.append("")
    lines.append("61–90 días (consolidación)")
    lines.append("- Objetivo: 2–3 clientes/proyectos o 1 contrato estable.")
    lines.append("- Nociones de automatización ligera (macros/fórmulas). Documentar KPIs.")

    # Consejos y herramientas
    lines.append("")
    lines.append("## Consejos prácticos de búsqueda")
    lines.append("- Filtrar por remoto y palabras clave: data entry, back office, data quality, transcripción, etiquetado.")
    lines.append("- Preparar mensajes cortos para candidatura fría y plataformas freelance.")
    lines.append("- Llevar registro de candidaturas y seguimientos a 7–10 días.")
    lines.append("")
    lines.append("## Herramientas útiles")
    lines.append("- Excel/Sheets; Airtable/Notion; OCR básico; Trello/Asana; Gmail, Slack/Teams.")

    # Juegos completados y capitalización
    lines.append("")
    lines.append("## Juegos completados y cómo capitalizarlos")
    for s in _take(sk_sorted, 4):
        lines.append(f"- {s['name']}: aplicar en entregables y SOPs para evidenciar valor.")

    # Frases listas
    lines.append("")
    lines.append("## Frases listas (para propuestas y LinkedIn)")
    lines.append("Titular: Data Entry | QA de Datos | Back-office (100% remoto)")
    lines.append("Acerca de: Capturo y depuro datos con precisión y tiempos fiables. Experiencia en proyectos internacionales (Excel/Sheets, OCR, QA). Busco aportar orden y métricas claras a equipos remotos.")

    # Mensaje final
    lines.append("")
    lines.append("## Mensaje final")
    lines.append("Base sólida para datos y operaciones remotas. Con un CV cuantificado, un LinkedIn claro y 2–3 pruebas de valor, puedes convertir la experiencia en contratos estables en 8–12 semanas.")

    return "\n".join(lines)


def generar_informe_prueba(
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
    Genera un informe de prueba profesional cuando Azure OpenAI no está configurado
    IMPORTANTE: Los minijuegos y CV son obligatorios para todos los candidatos
    """
    
    # Importar PromptConfig para usar el prompt centralizado
    try:
        from .prompt_config import PromptConfig
    except ImportError:
        from prompt_config import PromptConfig
    
    # Usar el prompt centralizado para mantener consistencia
    prompt = PromptConfig.get_employability_report_prompt(
        candidate_data=candidate_data,
        soft_skills_data=soft_skills_data,
        cv_data=cv_data,
        job_preferences_data=job_preferences_data,
        employability_score=employability_score,
        level=level,
        completed_games=completed_games,
        languages_data=languages_data
    )
    
    # Generar informe de prueba basado en el prompt centralizado
    # pero adaptado para modo de prueba (sin llamar a Azure OpenAI)
    return f"""
# 📋 Informe de Empleabilidad Profesional - MODO PRUEBA

**NOTA IMPORTANTE:** Este es un informe de prueba generado porque Azure OpenAI no está configurado. Para obtener un análisis completo y personalizado con inteligencia artificial, sigue las instrucciones de configuración.

## 1. DATOS PERSONALES BÁSICOS
- **Nombre**: {candidate_data.get('fullName', 'No consta')}
- **Email**: {candidate_data.get('email', 'No consta')}
- **Teléfono**: {candidate_data.get('phone', 'No consta')}
- **Ubicación**: {candidate_data.get('location', 'No consta')}
- **Certificado de discapacidad**: {'Sí' if candidate_data.get('hasDisabilityCertificate') else 'No' if candidate_data.get('hasDisabilityCertificate') is False else 'No consta'}

## 2. RESUMEN DEL PERFIL
Perfil profesional con puntuación de empleabilidad de {employability_score}/100, {level}. Los minijuegos han sido completados exitosamente y el CV ha sido analizado por las herramientas de IA.

## 3. RESUMEN DEL CV
- **Experiencia laboral**: {len(cv_data.get('sections', {}).get('experience', []))} posiciones detectadas
- **Formación académica**: {len(cv_data.get('sections', {}).get('education', []))} elementos educativos
- **Idiomas**: {len(cv_data.get('sections', {}).get('languages', []))} idiomas identificados
- **Software/Herramientas**: {len(cv_data.get('sections', {}).get('software', []))} herramientas detectadas

## 4. FORTALEZAS (CRUZANDO MINIJUEGOS Y CV)
- **Habilidades soft evaluadas**: {len(soft_skills_data)} competencias evaluadas en minijuegos
- **Competencias identificadas**: Basadas en CV y evaluación de minijuegos
- **Puntos fuertes**: Análisis disponible de soft skills y experiencia

## 5. ÁREAS DE MEJORA Y CONSEJOS (PRIORIZADAS Y ACCIONABLES)
- **Oportunidades de desarrollo**: Basadas en resultados de minijuegos y análisis de CV
- **Consejos específicos**: Disponibles tras configuración completa de IA
- **Enfoque constructivo**: Implementado en el sistema

## 6. ANÁLISIS DEL CV CON PUNTUACIÓN 1–5 POR APARTADO
**Estructura:** ★★★☆☆ (Regular) - Análisis básico disponible
**Claridad:** ★★★☆☆ (Regular) - Información estructurada
**Coherencia:** ★★★☆☆ (Regular) - Datos organizados
**Información clave:** ★★★☆☆ (Regular) - Contenido procesado
**Ortografía:** ★★★☆☆ (Regular) - Revisión básica

*Consejos detallados disponibles tras configuración de IA completa.*

## 7. ENTORNOS DE TRABAJO IDEALES
- **Modalidad preferida**: {', '.join(job_preferences_data.get('work_modes', ['No especificado']))}
- **Disponibilidad**: {job_preferences_data.get('availability', 'No especificado')}
- **Relocalización**: {'Sí' if job_preferences_data.get('relocation') else 'No' if job_preferences_data.get('relocation') is False else 'No consta'}

## 8. ROLES PROFESIONALES SUGERIDOS (ALINEADOS CON EXPERIENCIA Y PREFERENCIAS)
- **Puestos compatibles**: Análisis disponible según CV y preferencias
- **Sectores**: {', '.join(job_preferences_data.get('desired_sectors', ['No especificado']))}
- **Modalidad de trabajo**: {', '.join(job_preferences_data.get('work_modes', ['No especificado']))}

## 9. PLAN DE ACCIÓN A CORTO, MEDIO Y LARGO PLAZO
**Corto plazo (0-30 días):**
- Configurar Azure OpenAI para análisis completo
- Probar funcionalidades de IA
- Validar calidad de informes

**Medio plazo (1-3 meses):**
- Optimizar prompts de IA
- Implementar feedback de usuarios
- Mejorar análisis de CV

**Largo plazo (3-6+ meses):**
- Expandir funcionalidades
- Integrar análisis avanzado
- Desarrollar recomendaciones personalizadas

## 10. CONSEJOS DE BÚSQUEDA DE EMPLEO (CV, NETWORKING, PLATAFORMAS, ENTREVISTAS)
- **Estrategias activas**: Recomendaciones disponibles
- **Plataformas de empleo**: LinkedIn, InfoJobs, Empléate
{'**Plataformas inclusivas**: Inserta Empleo, Plena Inclusión' if candidate_data.get('hasDisabilityCertificate') else ''}

## 11. HERRAMIENTAS ÚTILES Y TECNOLOGÍA
- **Plataformas de formación**: Coursera, edX, Google Digital
- **Herramientas tecnológicas**: Integradas
- **Recursos profesionales**: Accesibles

## 12. JUEGOS COMPLETADOS (Y QUÉ EVIDENCIAN)
{', '.join(completed_games) if completed_games else 'No consta'} - Evaluación de soft skills completada

## 13. FRASE FINAL DE CIERRE MOTIVACIONAL Y PERSONALIZADA
Este informe se ha realizado teniendo en cuenta toda la información que nos has proporcionado y tus preferencias laborales. Aprovecha tus fortalezas y confía en tu potencial. ¡Mucha suerte!

---

**NOTA IMPORTANTE:** Este es un informe de prueba generado porque Azure OpenAI no está configurado. Para obtener un análisis completo y personalizado con inteligencia artificial, sigue las instrucciones de configuración en `azure_openai_setup.md`.

**IMPORTANTE:** Los minijuegos y CV son obligatorios para todos los candidatos y han sido completados exitosamente.

**Fecha de generación:** {datetime.now().strftime('%d/%m/%Y a las %H:%M')}
"""

def generar_informe(
    candidate_data: dict,
    soft_skills_data: list,
    cv_data: dict,
    job_preferences_data: dict,
    employability_score: int,
    level: str,
    completed_games: list,
    languages_data: list,
    return_json: bool = False
) -> str | tuple[str, dict]:
    """
    Genera un informe de empleabilidad usando Azure OpenAI o modo de prueba
    IMPORTANTE: Los minijuegos y CV son obligatorios para todos los candidatos
    """
    
    if not AZURE_OPENAI_CONFIGURED:
        logger.warning("⚠️ Azure OpenAI no configurado - usando modo de prueba")
        md = generar_informe_prueba(
            candidate_data, soft_skills_data, cv_data, job_preferences_data,
            employability_score, level, completed_games, languages_data
        )
        return (md, {}) if return_json else md
    
    try:
        # Verificar que las variables no sean None
        if not all([API_KEY, ENDPOINT, DEPLOYMENT]):
            raise ValueError("Variables de Azure OpenAI no configuradas")
        
        # Configurar cliente Azure OpenAI con type assertions
        assert API_KEY is not None
        assert ENDPOINT is not None
        assert DEPLOYMENT is not None
        
        client = AzureOpenAI(
            api_key=API_KEY,
            api_version=API_VERSION,
            azure_endpoint=ENDPOINT,
            timeout=300.0
        )
        
        # Cargar feedback previo
        feedback_previo = cargar_feedback_previo()
        
        # Importar PromptConfig para usar el prompt centralizado
        try:
            from .prompt_config import PromptConfig
        except ImportError:
            from prompt_config import PromptConfig
        
        # INYECTAR diagnóstico determinista y estructura CV
        try:
            try:
                from .cv_structure_analyzer import compute_review_from_text_sections, review_to_ui_diagnostico
            except ImportError:
                from cv_structure_analyzer import compute_review_from_text_sections, review_to_ui_diagnostico
            # Asegurar rawText y sections
            raw_text = (cv_data or {}).get("rawText") or (cv_data or {}).get("raw_text") or ""
            sections = (cv_data or {}).get("sections") or {}
            review = compute_review_from_text_sections(raw_text, sections)
            cv_ui_diag = review_to_ui_diagnostico(review)
            # Normalizar style_score
            if "spelling_style_score" in cv_ui_diag and "style_score" not in cv_ui_diag:
                cv_ui_diag["style_score"] = cv_ui_diag["spelling_style_score"]

            cv_structured = {
                "profile": (sections.get("profile") or ""),
                "experience": (sections.get("experience") or []),
                "education": (sections.get("education") or []),
                "languages": (sections.get("languages") or []),
                "software": (sections.get("software") or sections.get("skills") or []),
                "contact": (sections.get("contact") or {}),
            }
            cv_data = dict(cv_data or {})
            cv_data["rawText"] = raw_text
            cv_data["cv_structured"] = cv_structured
            cv_data["cv_diagnostico_ui"] = cv_ui_diag
        except Exception as _e:
            logger.warning(f"No se pudo computar diagnóstico determinista: {_e}")
            cv_ui_diag = {}

        analysis_block = PromptConfig.make_cv_analysis_block(cv_ui_diag, cv_data)
        prompt = PromptConfig.get_employability_report_prompt(
            candidate_data=candidate_data,
            soft_skills_data=soft_skills_data,
            cv_data=cv_data,
            job_preferences_data=job_preferences_data,
            employability_score=employability_score,
            level=level,
            completed_games=completed_games,
            languages_data=languages_data,
            analysis_block=analysis_block
        )
        
        # Llamar a Azure OpenAI
        # Sanitizar el esquema antes de enviarlo
        report_schema = PromptConfig.get_report_schema()
        
        def _allow_null(t):
            """Permite null en tipos para hacer campos opcionales"""
            if isinstance(t, list):
                return t if "null" in t else t + ["null"]
            if isinstance(t, str):
                return [t, "null"]
            return t

        def harden_schema(node: dict, _depth: int = 0) -> dict:
            """
            Sanitiza un JSON Schema para Azure OpenAI strict mode:
            1. Cierra todos los objetos con additionalProperties: false
            2. Hace required = todas las propiedades (evita "Missing 'name'/'emails'/...")
            3. Permite null en tipos para campos opcionales (pero NO en la raíz)
            """
            if not isinstance(node, dict):
                return node

            t = node.get("type")

            # Objetos: cerrar y forzar required = todas las props
            if t == "object":
                props = node.get("properties", {}) or {}
                node.setdefault("additionalProperties", False)
                node["required"] = list(props.keys())  # <= evita "Missing 'name'/'emails'/...
                # Recorremos propiedades incrementando profundidad
                for k, v in list(props.items()):
                    node["properties"][k] = harden_schema(v, _depth + 1)
                # 👇 En la raíz mantenemos "object" a pelo; en niveles internos permitimos null
                node["type"] = "object" if _depth == 0 else _allow_null("object")

            elif t == "array":
                if "items" in node:
                    node["items"] = harden_schema(node["items"], _depth + 1)
                node["type"] = "array" if _depth == 0 else _allow_null("array")

            elif t in ("string", "number", "integer", "boolean"):
                node["type"] = t if _depth == 0 else _allow_null(t)

            # Combinadores, si los hubiera
            for key in ("oneOf", "anyOf", "allOf"):
                if key in node and isinstance(node[key], list):
                    node[key] = [harden_schema(x, _depth + 1) if isinstance(x, dict) else x for x in node[key]]

            return node
        
        report_schema = harden_schema(report_schema)
        # 🔧 Azure SO no admite ['object','null'] en la raíz
        if isinstance(report_schema.get("type"), list):
            report_schema["type"] = "object"
        
        response = client.chat.completions.create(
            model=DEPLOYMENT,
            messages=[
                {"role": "system", "content": PromptConfig.get_system_prompt()},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=3000,
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "EmployabilityReport",
                    "schema": report_schema,
                    "strict": True
                }
            }
        )
        
        content = response.choices[0].message.content

        # Si la respuesta es JSON válido, lo convertimos; si no, o si falta contenido clave, renderizamos determinista
        try:
            json_response = json.loads(content) if (content and content.strip().startswith('{')) else {}
        except Exception:
            json_response = {}

        # Render determinista basado 100% en datos reales disponibles
        md_deterministic = render_real_report_markdown(
            candidate_data=candidate_data,
            soft_skills_data=soft_skills_data,
            cv_data=cv_data,
            job_preferences_data=job_preferences_data,
            languages_data=languages_data,
            cv_ui_diag=cv_ui_diag,
        )

        # Si hay JSON del modelo y es útil, se puede adjuntar como anexo o ignorar; priorizamos determinista
        return (md_deterministic, json_response) if return_json else md_deterministic
        else:
            # Si no es JSON, devolver también en formato esperado
            md = content if content else generar_informe_prueba(
                candidate_data, soft_skills_data, cv_data, job_preferences_data,
                employability_score, level, completed_games, languages_data
            )
            return (md, {}) if return_json else md
        
    except Exception as e:
        logger.error(f"❌ Error generando informe con Azure OpenAI: {str(e)}")
        logger.info("🔄 Usando modo de prueba como fallback")
        return generar_informe_prueba(
            candidate_data, soft_skills_data, cv_data, job_preferences_data,
            employability_score, level, completed_games, languages_data
        )


def attach_analysis_json_to_prompt(cv_data: dict, report_id: Optional[str] = None) -> dict:
    """Carga analysis.json si existe y lo adjunta en cv_data['analysis_json'] para consumo de la IA."""
    try:
        analysis = None
        # Preferencia: si viene ruta directa en cv_data
        if isinstance(cv_data, dict) and cv_data.get('analysis_json'):
            return cv_data
        # Buscar por report_id
        if report_id:
            local_path = os.path.join(os.getcwd(), 'reports', report_id, 'analysis.json')
            if os.path.exists(local_path):
                with open(local_path, 'r', encoding='utf-8') as fh:
                    analysis = json.load(fh)
        # Si no, intentar inline si viene en cv_data
        if not analysis and isinstance(cv_data, dict) and cv_data.get('analysis'):
            analysis = cv_data.get('analysis')
        if analysis:
            cv_data = dict(cv_data)
            cv_data['analysis_json'] = analysis
        return cv_data
    except Exception as e:
        logger.warning(f"No se pudo adjuntar analysis_json al prompt: {e}")
        return cv_data

def cargar_feedback_previo():
    """
    Carga el feedback previo de los usuarios
    """
    feedback_file = "feedback_ia.json"
    if not os.path.exists(feedback_file):
        return ""
    
    try:
        with open(feedback_file, 'r', encoding='utf-8') as f:
            feedbacks = json.load(f)
        
        if not feedbacks:
            return ""
        
        def es_util(fb: dict) -> bool:
            r = fb.get('rating')
            try:
                if isinstance(r, (int, float)) and float(r) >= 4:
                    return True
            except Exception:
                pass
            label = str(fb.get('ratingLabel') or fb.get('rating') or '').strip().lower()
            return label in ('útil','util','useful')

        feedbacks_utiles = [f for f in feedbacks if es_util(f)]
        
        if not feedbacks_utiles:
            return ""
        
        feedbacks_recientes = feedbacks_utiles[-5:]
        
        feedback_text = "\n\nFEEDBACK PREVIO DE USUARIOS:\n"
        for i, feedback in enumerate(feedbacks_recientes, 1):
            feedback_text += f"\n{i}. {feedback.get('comment', 'Sin comentarios')}"
        
        return feedback_text
        
    except Exception as e:
        logger.warning(f"⚠️ Error cargando feedback previo: {str(e)}")
        return ""
