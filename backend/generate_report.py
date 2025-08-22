# generate_report.py
# -*- coding: utf-8 -*-
"""
Generador de informe IA _determinista_ y robusto a partir del prompt de back-end.
No requiere claves ni servicios externos. Siempre devuelve un dict con:
{
  "report": {...},
  "recommendations": [...],
  "level": "Bajo|Medio|Alto",
  "employabilityScore": int
}
"""

from __future__ import annotations
import json
import re
from typing import Any, Dict, List, Tuple

# ----------------------------
# Utilidades de parsing seguro
# ----------------------------

_SOFT_LINE = re.compile(
    r"^\s*-\s*(?P<skill>[^:]+):\s*(?P<score>\d{1,3})\s*/\s*100"
    r"(?:\s*\((?P<level>[^)]+)\))?\s*$",
    flags=re.IGNORECASE,
)

SECTION_HEADERS = {
    "resumen": re.compile(r"^\s*1\)\s*RESUMEN\s+EJECUTIVO\s*$", re.IGNORECASE),
    "soft": re.compile(r"^\s*2\)\s*SOFT\s+SKILLS\s*$", re.IGNORECASE),
    "cv": re.compile(r"^\s*3\)\s*CV\s+ANALIZADO\s*$", re.IGNORECASE),
    "prefs": re.compile(r"^\s*4\)\s*PREFERENCIAS\s+LABORALES\s*$", re.IGNORECASE),
    "games": re.compile(r"^\s*5\)\s*JUEGOS\s+COMPLETADOS\s*$", re.IGNORECASE),
    # ignoramos 6..12 si existen
    "closing": re.compile(r"^\s*13\)\s*FRASE\s+FINAL\s*$", re.IGNORECASE),
}

def _split_sections(prompt: str) -> Dict[str, List[str]]:
    """
    Divide el prompt por secciones numeradas que esperamos (1..5 y 13).
    Devuelve map {clave: [lineas]} sin los encabezados.
    """
    lines = prompt.splitlines()
    buckets: Dict[str, List[str]] = {k: [] for k in SECTION_HEADERS.keys()}

    current_key: str | None = None
    for raw in lines:
        # Detecta encabezado
        hit = None
        for key, rx in SECTION_HEADERS.items():
            if rx.match(raw):
                current_key = key
                hit = True
                break
        if hit:
            continue

        if current_key:
            buckets[current_key].append(raw)

    return buckets

def _parse_soft_skills(lines: List[str]) -> Tuple[List[Dict[str, Any]], int]:
    """
    Extrae soft skills en el formato
    "- Comunicación: 85/100 (Avanzado)"
    Devuelve (lista, media_entera_0_100)
    """
    parsed: List[Dict[str, Any]] = []
    scores: List[int] = []
    for ln in lines:
        m = _SOFT_LINE.match(ln.strip())
        if not m:
            continue
        skill = m.group("skill").strip()
        score = int(m.group("score"))
        level = (m.group("level") or "").strip() or None
        # acota score a 0..100
        score = max(0, min(100, score))
        parsed.append({"skill": skill, "score": score, "level": level})
        scores.append(score)

    avg = int(round(sum(scores) / len(scores))) if scores else 0
    return parsed, avg

def _score_to_level(score: int) -> str:
    if score >= 75:
        return "Alto"
    if score >= 50:
        return "Medio"
    return "Bajo"

def _clean_join(lines: List[str]) -> str:
    # Junta líneas, eliminando múltiples blancos
    text = "\n".join([ln.rstrip() for ln in lines]).strip()
    return re.sub(r"\n{3,}", "\n\n", text) if text else ""

def _extract_list_from_lines(lines: List[str]) -> List[str]:
    """
    Si las líneas tienen formato de lista con guiones, extrae cada ítem.
    """
    out: List[str] = []
    for ln in lines:
        m = re.match(r"^\s*-\s*(.+?)\s*$", ln)
        if m:
            out.append(m.group(1).strip())
    return out

# ----------------------------
# Núcleo público
# ----------------------------

def generar_informe(prompt: str | Dict[str, Any]) -> Dict[str, Any]:
    """
    Entrada: prompt (str) tal y como lo construye main.build_prompt(...)
    Salida: dict conforme a la UI/PDF.

    Nunca devuelve None. Nunca accede a .get() sobre valores no dict.
    """
    if prompt is None:
        # Fallback ultra seguro
        return {
            "report": {
                "resumen_ejecutivo": "No se recibió información suficiente.",
                "soft_skills": [],
                "cv_analizado": "Sin análisis.",
                "preferencias_laborales": "No especificadas.",
                "juegos_completados": [],
                "frase_final": "Define un objetivo profesional y comienza por acciones concretas la próxima semana.",
            },
            "recommendations": [],
            "level": "Bajo",
            "employabilityScore": 0,
        }

    # Si por error llega un dict (no debería, pero lo soportamos)
    if isinstance(prompt, dict):
        # Intentamos serializarlo y continuar, para mantener una salida homogénea.
        prompt = json.dumps(prompt, ensure_ascii=False)

    # Parseo de secciones
    sec = _split_sections(prompt)

    # 1) Resumen + nombre si está en la línea siguiente
    resumen_text = _clean_join(sec.get("resumen", []))
    # intenta rescatar "Nombre: X" si existe en el prompt original
    m_name = re.search(r"(?im)^\s*Nombre\s*:\s*(.+?)\s*$", prompt)
    nombre = m_name.group(1).strip() if m_name else None
    if nombre and "Nombre:" not in resumen_text:
        resumen_text = ("Nombre: " + nombre + "\n" + resumen_text).strip()

    # 2) Soft skills
    soft_list, soft_avg = _parse_soft_skills(sec.get("soft", []))
    nivel = _score_to_level(soft_avg)

    # 3) CV analizado (bloque entero tal cual lo generó el back, si existe)
    cv_text = _clean_join(sec.get("cv", [])) or "CV ANALIZADO\n- No se pudo recuperar el detalle."

    # 4) Preferencias laborales
    prefs_text = _clean_join(sec.get("prefs", [])) or "PREFERENCIAS LABORALES\n- No especificadas."

    # 5) Juegos completados
    games = _extract_list_from_lines(sec.get("games", []))
    # Si vino "- No consta", dejamos lista vacía
    games = [] if any("no consta" in (g or "").lower() for g in games) else games

    # 13) Frase final
    cierre = _clean_join(sec.get("closing", [])) or \
        "Mantén una búsqueda activa, actualiza tu CV con logros medibles y crea una rutina semanal de networking."

    # Recomendaciones básicas derivadas del contenido
    recs: List[str] = []
    if soft_avg < 50:
        recs.append("Refuerza las competencias con cursos breves y práctica guiada (p.ej., comunicación y trabajo en equipo).")
    if "CV ANALIZADO" in cv_text and "No se ha podido" in cv_text:
        recs.append("Sube un CV en PDF legible y con fechas, funciones y logros concretos (STAR).")
    if not games:
        recs.append("Completa los juegos de evaluación para enriquecer tu perfil de soft skills.")
    if not recs:
        recs = [
            "Prioriza 3 vacantes objetivo y adapta tu CV con logros cuantificables.",
            "Refuerza tu perfil de LinkedIn y pide 2-3 recomendaciones recientes.",
        ]

    # Construcción del informe
    report: Dict[str, Any] = {
        "resumen_ejecutivo": resumen_text or "Sin resumen disponible.",
        "soft_skills": soft_list,                     # lista [{skill, score, level?}]
        "cv_analizado": cv_text,                      # bloque multilínea
        "preferencias_laborales": prefs_text,         # bloque multilínea
        "juegos_completados": games,                  # lista de textos
        "frase_final": cierre,                        # cierre breve
    }

    # Puntuación global basada en las soft skills
    employability = int(soft_avg)

    return {
        "report": report,
        "recommendations": recs,
        "level": nivel,
        "employabilityScore": employability,
    }
