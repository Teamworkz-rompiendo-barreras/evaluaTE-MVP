# generate_report.py
# Deterministic report builder that parses the composed prompt (string) and produces
# a structured dictionary the frontend expects. No external AI calls here.

from __future__ import annotations
import re
from typing import Dict, Any, List, Tuple, Optional

STAR_FULL = "★"
STAR_EMPTY = "☆"

def _extract_section(text: str, title: str) -> str:
    pattern = rf"(?mi)^\s*{re.escape(title)}\s*$"
    m = re.search(pattern, text)
    if not m:
        pat2 = rf"(?mi)^\s*\d+\)\s*{re.escape(title)}\s*$"
        m = re.search(pat2, text)
    if not m:
        return ""
    start = m.end()
    nxt = re.search(r"(?m)^\s*\d+\)\s*[A-ZÁÉÍÓÚÜÑ].*$", text[start:])
    end = start + (nxt.start() if nxt else len(text[start:]))
    return text[start:end].strip()

def _get_name(text: str) -> Optional[str]:
    m = re.search(r"(?mi)^\s*Nombre:\s*(.+)$", text)
    return m.group(1).strip() if m else None

def _parse_softskills(section: str) -> List[Dict[str, Any]]:
    out=[]
    for line in section.splitlines():
        line=line.strip(" -•\t")
        m = re.match(r"(.+?):\s*(\d{1,3})/100(?:\s*\((.+?)\))?", line)
        if m:
            skill=m.group(1).strip()
            score=int(m.group(2))
            level=(m.group(3) or "").strip() or None
            out.append({"skill":skill,"score":score,"level":level})
    return out

def _stars_to_int(stars: str) -> int:
    full = stars.count(STAR_FULL)
    empty = stars.count(STAR_EMPTY)
    if full+empty==0:
        m = re.search(r"(\d)\s*/\s*5", stars)
        if m:
            return int(m.group(1))
    return max(0, min(5, full))

def _parse_cv_analizado(section: str) -> Dict[str, Any]:
    res = {"summary": None, "strengths": [], "weaknesses": [], "feedback": None, "stars": None}
    m = re.search(r"(?mi)^Resumen:\s*(.+)$", section)
    if m:
        res["summary"]=m.group(1).strip()
    stars={}
    for key in [("formato","Formato"),("claridad","Claridad"),("coherencia","Coherencia"),("informacion_clave","Información clave"),("ortografia","Ortografía")]:
        m = re.search(rf"(?mi)^{re.escape(key[1])}:\s*(.+)$", section)
        if m:
            stars[key[0]]=_stars_to_int(m.group(1))
    if stars:
        res["stars"]=stars
    if re.search(r"(?mi)^Fortalezas:\s*$", section):
        body = section[re.search(r"(?mi)^Fortalezas:\s*$", section).end():]
        stop = re.search(r"(?mi)^(Áreas de mejora|Correcciones/Acciones):", body)
        body = body[:stop.start()] if stop else body
        for line in body.splitlines():
            line=line.strip()
            if line.startswith("-"):
                res["strengths"].append(line[1:].strip())
    if re.search(r"(?mi)^Áreas de mejora:\s*$", section):
        body = section[re.search(r"(?mi)^Áreas de mejora:\s*$", section).end():]
        stop = re.search(r"(?mi)^Correcciones/Acciones:", body)
        body = body[:stop.start()] if stop else body
        for line in body.splitlines():
            line=line.strip()
            if line.startswith("-"):
                res["weaknesses"].append(line[1:].strip())
    if re.search(r"(?mi)^Correcciones/Acciones:\s*$", section):
        body = section[re.search(r"(?mi)^Correcciones/Acciones:\s*$", section).end():]
        lines=[]
        for line in body.splitlines():
            line=line.strip(" -")
            if line:
                lines.append("• "+line)
        if lines:
            res["feedback"]="\n".join(lines)
    return res

def _parse_prefs(section: str) -> Dict[str, Any]:
    prefs={}
    def grab(label, key):
        m = re.search(rf"(?mi)^\s*-\s*{re.escape(label)}:\s*(.+)$", section)
        if m:
            prefs[key]=m.group(1).strip()
    grab("Roles/Sectores","areas")
    grab("Modalidad","workMode")
    grab("Disponibilidad","availability")
    grab("Relocalización","willingToRelocate")
    grab("Certificado de discapacidad","hasDisabilityCert")
    m = re.search(r"(?mi)^\s*-\s*Necesidades:\s*(.+)$", section)
    if m:
        prefs["needs"]=[x.strip() for x in re.split(r",|;|·", m.group(1)) if x.strip()]
    return prefs

def _parse_juegos(section: str) -> List[str]:
    items=[]
    for line in section.splitlines():
        t=line.strip(" -•\t")
        if not t: 
            continue
        if "," in t and not re.search(r"\s", t.split(",")[0].strip()):
            items.extend([x.strip() for x in t.split(",") if x.strip()])
        else:
            items.append(t)
    seen=set(); out=[]
    for it in items:
        if it not in seen:
            out.append(it); seen.add(it)
    return out

def _build_resumen_ejecutivo(name: Optional[str], soft: List[Dict[str,Any]], cv: Dict[str,Any], prefs: Dict[str,Any]) -> str:
    texto=[]
    if soft:
        top = sorted(soft, key=lambda s:s["score"], reverse=True)[:2]
        low = sorted(soft, key=lambda s:s["score"])[:2]
        if top:
            texto.append(f"Perfil con fortaleza principal en {top[0]['skill']} ({top[0]['score']}/100).")
            if len(top)>1:
                texto.append(f"También destaca en {top[1]['skill']} ({top[1]['score']}/100).")
        if low:
            texto.append(f"Áreas a potenciar: {', '.join([f\"{x['skill']} ({x['score']}/100)\" for x in low])}.")
    if prefs:
        pref_bits=[]
        if prefs.get('workMode'):
            pref_bits.append(f"preferencia por trabajo {prefs['workMode']}")
        if prefs.get('availability'):
            pref_bits.append(f"disponibilidad {prefs['availability']}")
        if 'willingToRelocate' in prefs:
            pref_bits.append(f"relocalización: {prefs['willingToRelocate']}")
        if pref_bits:
            texto.append("Preferencias: " + ", ".join(pref_bits) + ".")
    if cv.get("summary"):
        texto.append(cv["summary"])
    return " ".join(texto) or "Resumen no disponible."

def generar_informe(prompt: str) -> Dict[str, Any]:
    name = _get_name(prompt)
    soft = _parse_softskills(_extract_section(prompt, "SOFT SKILLS"))
    cv_section = _extract_section(prompt, "CV ANALIZADO")
    cv = _parse_cv_analizado(cv_section) if cv_section else {}
    prefs = _parse_prefs(_extract_section(prompt, "PREFERENCIAS LABORALES"))
    juegos = _parse_juegos(_extract_section(prompt, "JUEGOS COMPLETADOS"))

    resumen_ejecutivo = _build_resumen_ejecutivo(name, soft, cv, prefs)

    report: Dict[str, Any] = {
        "datos_personales": {
            "nombre": name or "No consta",
            "ubicacion": None,
            "email": None,
            "telefono": None,
            "discapacidad": prefs.get("hasDisabilityCert", None),
        },
        "resumen_perfil": cv.get("summary") or "No consta",
        "resumen_cv": {
            "experiencia": [],
            "formacion": [],
            "idiomas": [],
            "software": [],
            "observaciones": ""
        },
        "fortalezas_clave": [f"{s}" for s in cv.get("strengths", [])] or [],
        "areas_mejora": [f"{w}" for w in cv.get("weaknesses", [])] or [],
        "diagnostico_cv": {
            "formato": cv.get("stars",{}).get("formato"),
            "claridad": cv.get("stars",{}).get("claridad"),
            "coherencia": cv.get("stars",{}).get("coherencia"),
            "informacion_clave": cv.get("stars",{}).get("informacion_clave"),
            "ortografia": cv.get("stars",{}).get("ortografia"),
            "feedback": cv.get("feedback")
        },
        "entornos_ideales": "Tareas con métricas claras y comunicación asincrónica.",
        "roles_sugeridos": [],
        "plan_accion": {
            "corto_plazo": [],
            "medio_plazo": [],
            "largo_plazo": []
        },
        "consejos_busqueda": [],
        "herramientas_utiles": [],
        "juegos_completados": juegos,
        "frase_final": "Sigue consolidando evidencia cuantificable y mantén un ritmo de candidaturas sostenido.",
        "resumen_ejecutivo": resumen_ejecutivo,
        "analisis_perfil": {"soft_skills": soft},
        "evaluacion_cv": cv,
    }

    if soft:
        names=[s["skill"].lower() for s in soft]
        if "data" in " ".join(names) or "analítico" in " ".join(names):
            report["roles_sugeridos"].append("Data Entry / Etiquetado de datos — Remoto")
        report["roles_sugeridos"] += ["Asistente administrativo remoto", "Gestión de cuentas junior"]

    report["plan_accion"]["corto_plazo"] = [
        "Actualizar CV con logros cuantificados y enlaces.",
        "Optimizar LinkedIn y preparar portfolio ligero (2–3 muestras).",
        "Ejecutar 10 candidaturas/semana a roles alineados."
    ]
    report["plan_accion"]["medio_plazo"] = [
        "Mejorar habilidades clave detectadas (p. ej., análisis de datos, influencia).",
        "Ampliar red de contactos con mensajes breves de valor."
    ]
    report["plan_accion"]["largo_plazo"] = [
        "Especializarse en un flujo (p. ej., QA de datos) y documentar SOPs."
    ]
    report["consejos_busqueda"] = [
        "Usa palabras clave del rol objetivo para superar ATS.",
        "Personaliza 1 párrafo por candidatura con prueba de valor adjunta."
    ]
    report["herramientas_utiles"] = [
        "Excel/Sheets", "Airtable/Notion", "OCR básico", "Trello/Asana", "Slack/Teams"
    ]

    return report
