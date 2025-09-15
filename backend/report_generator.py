from typing import Any, Dict, List

STAR = "★"
EMPTY = "☆"


def stars(n: int) -> str:
    n = max(0, min(5, int(n)))
    return STAR * n + EMPTY * (5 - n)


def render_informe_estructurado(report: Dict[str, Any]) -> str:
    """Renderiza un informe estructurado en texto/markdown usando NewReportSchema."""
    personal = report.get("personal_data") or {}
    cv_analysis = report.get("cv_analysis") or {}

    out: List[str] = []

    out.append("Resumen ejecutivo\n")
    out.append(f"{report.get('summary', '')}\n")

    out.append("Datos personales\n")
    out.append(f"Nombre: {personal.get('name', 'No consta')}\n")
    out.append(f"Ubicación: {personal.get('location', 'No consta')}\n")
    out.append(f"Email: {personal.get('email', 'No consta')}\n")
    out.append(f"Teléfono: {personal.get('phone', 'No consta')}\n")
    out.append(f"Certificado de discapacidad: {personal.get('disability_certificate', 'No')}\n")

    out.append("\nResumen de perfil\n")
    out.append(f"{report.get('profile_summary', '')}\n")

    out.append("\nResumen del CV\n")
    out.append(f"{report.get('cv_summary', '')}\n")

    cv_details = report.get("cv_details") or {}

    def _render_detail_section(title: str, items: Any) -> None:
        values = []
        if isinstance(items, list):
            values = [str(item) for item in items if item not in (None, "")]
        elif items:
            values = [str(items)]
        if not values:
            return
        out.append(f"\n{title}\n")
        for entry in values:
            out.append(f"- {entry}\n")

    _render_detail_section("Experiencia destacada", cv_details.get("experience"))
    _render_detail_section("Formación", cv_details.get("education"))
    _render_detail_section("Idiomas", cv_details.get("languages"))
    _render_detail_section("Herramientas y tecnología", cv_details.get("tools"))

    out.append("\nFortalezas clave\n")
    for f in report.get("strengths", []):
        out.append(f"- {f}\n")

    out.append("\nÁreas de mejora priorizadas\n")
    for area in report.get("improvement_areas", []):
        if isinstance(area, dict):
            label = area.get("area")
            action = area.get("suggested_action")
            if label and action:
                out.append(f"- {label}: {action}\n")
            elif label:
                out.append(f"- {label}\n")
        else:
            out.append(f"- {area}\n")

    out.append("\nDiagnóstico del CV (estrellas)\n")
    out.append(f"Estructura: {stars(cv_analysis.get('structure_score', 0))}\n")
    out.append(f"Claridad: {stars(cv_analysis.get('clarity_score', 0))}\n")
    out.append(f"Coherencia: {stars(cv_analysis.get('coherence_score', 0))}\n")
    out.append(f"Información clave: {stars(cv_analysis.get('key_info_score', 0))}\n")
    out.append(f"Estilo: {stars(cv_analysis.get('style_score', 0))}\n")

    out.append("\nEntornos de trabajo ideales\n")
    out.append(f"{report.get('ideal_work_environment', '')}\n")

    out.append("\nRoles sugeridos\n")
    for r in report.get("suggested_roles", []):
        if isinstance(r, dict):
            line = f"- {r.get('role')} — {r.get('seniority')} — Remoto: {r.get('remote_viable')}"
            if r.get("reason"):
                line += f". Razón: {r.get('reason')}"
            out.append(line + "\n")
        else:
            out.append(f"- {r}\n")

    out.append("\nPlan de acción (30–60–90 días)\n")
    plan = report.get("action_plan") or {}
    short = plan.get("short_term", [])
    medium = plan.get("medium_term", [])
    long_term = plan.get("long_term", [])
    if short:
        out.append("0–30 días (bases)\n")
        for it in short:
            out.append(f"- {it}\n")
    if medium:
        out.append("31–60 días (tracción)\n")
        for it in medium:
            out.append(f"- {it}\n")
    if long_term:
        out.append("61–90 días (consolidación)\n")
        for it in long_term:
            out.append(f"- {it}\n")

    out.append("\nConsejos prácticos de búsqueda\n")
    advice = report.get("job_search_advice") or {}
    cv_opt = advice.get("cv_optimization")
    if cv_opt:
        if isinstance(cv_opt, list):
            out.append(f"CV: {', '.join(cv_opt)}\n")
        else:
            out.append(f"CV: {cv_opt}\n")
    letters = advice.get("letters_portfolio")
    if letters:
        out.append(f"Cartas/portfolio: {letters}\n")
    platforms = advice.get("recommended_platforms")
    if platforms:
        out.append(f"Plataformas: {', '.join(platforms)}\n")
    networking = advice.get("networking")
    if networking:
        out.append(f"Networking: {networking}\n")
    interview = advice.get("interview_tips")
    if interview:
        out.append(f"Entrevistas: {interview}\n")

    out.append("Herramientas útiles\n")
    tools = report.get("useful_tools") or {}
    for key in ["productivity", "job_search", "learning", "accessibility"]:
        vals = tools.get(key)
        if vals:
            out.append(f"{key.replace('_', ' ').title()}: {', '.join(vals)}\n")

    out.append("\nJuegos completados y cómo capitalizarlos\n")
    for j in report.get("completed_games", []):
        out.append(f"- {j}\n")

    out.append("\nMensaje final\n")
    out.append(f"{report.get('final_message', '')}\n")
    return "\n".join(out)

