#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
cv_structure_analyzer.py

Analizador determinista y ligero de la estructura del CV usado para el
apartado "Análisis del CV (1–5)" del informe. No depende del LLM y es
robusto ante entradas parciales.

Funciones principales:
- analyze_cv_structure(path): Extrae texto de un PDF con PyMuPDF y calcula
  métricas objetivas → puntuaciones 0–100 → estrellas 1–5.
- compute_review_from_text_sections(text, sections): Igual que el anterior
  pero usando texto y secciones ya extraídas (ideal para integrarse con
  /api/pdf/analyze-cv).
- review_to_ui_diagnostico(review): Mapea el resultado al formato
  esperado por el frontend en `diagnostico_cv`.

Las puntuaciones siguen 5 dimensiones: formato, claridad, coherencia,
información clave y ortografía.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple
import re

# Dependencias opcionales; el módulo funciona sin PyMuPDF
try:
    import fitz  # type: ignore
except Exception:  # pragma: no cover
    fitz = None  # type: ignore

try:
    from spellchecker import SpellChecker  # type: ignore
except Exception:  # pragma: no cover
    SpellChecker = None  # type: ignore

try:
    from dateparser import parse as parse_date  # type: ignore
except Exception:  # pragma: no cover
    parse_date = None  # type: ignore


def stars_from_score(score_0_100: float) -> int:
    """Convierte 0–100 a estrellas 1–5."""
    try:
        s = float(score_0_100)
    except Exception:
        s = 0.0
    if s < 20:
        return 1
    if s < 40:
        return 2
    if s < 60:
        return 3
    if s < 80:
        return 4
    return 5


SECTION_PATTERNS = {
    "experience": r"(?:experiencia|work\s+experience|professional\s+experience|trayectoria|empleo)s?",
    "education": r"(?:educaci[oó]n|education|formaci[oó]n)s?",
    "profile": r"(?:perfil|profile|resumen|summary)",
    "skills": r"(?:habilidades|skills|competencias|aptitudes)",
    "languages": r"(?:idiomas|languages)",
    "certs": r"(?:certificaciones?|certifications?)",
    "contact": r"(?:contacto|contact|datos\s+de\s+contacto)",
}


DATE_TOKEN_RE = re.compile(
    r"(?:(\d{4})|(?:\b(?:ene|feb|mar|abr|may|jun|jul|ago|sep|oct|nov|dic|jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\b\.?\s*\d{4}))",
    re.IGNORECASE,
)


def _avg_words_per_sentence(text: str) -> float:
    if not text:
        return 0.0
    # Cortes sencillos de frase
    sentences = re.split(r"[\.!?]+\s+", text)
    sentences = [s for s in sentences if s.strip()]
    words = re.findall(r"\p{L}+", text, flags=re.UNICODE)
    if not sentences:
        return float(len(words))
    return float(len(words)) / float(len(sentences))


def _bullet_count(text: str) -> int:
    return len(re.findall(r"(?m)^\s*[-•·]", text))


def _detect_language_basic(text: str) -> str:
    t = (text or "").lower()
    score_es = sum(1 for w in [" el ", " la ", " de ", " y ", " que "] if w in t)
    score_en = sum(1 for w in [" the ", " and ", " of ", " in ", " to "] if w in t)
    score_pt = sum(1 for w in [" de ", " e ", " que ", " para ", " com "] if w in t)
    if max(score_es, score_en, score_pt) == score_en:
        return "en"
    if max(score_es, score_en, score_pt) == score_pt:
        return "pt"
    return "es"


def _parse_any_date(txt: str) -> Optional[int]:
    """Devuelve año aproximado o None."""
    # Try dateparser if available
    if parse_date is not None:
        try:
            d = parse_date(txt, languages=["es", "en", "pt"])  # type: ignore[arg-type]
            if d:
                return d.year
        except Exception:
            pass
    # Fallback: busca un año
    m = re.search(r"\b(19|20)\d{2}\b", txt)
    return int(m.group(0)) if m else None


def _coherence_score_from_experience_lines(lines: List[str]) -> Tuple[float, str]:
    years: List[int] = []
    for ln in lines or []:
        years.extend([y for y in (_parse_any_date(m.group(0)) for m in DATE_TOKEN_RE.finditer(ln)) if y is not None])
    # Simplificación: comprobamos orden no creciente
    ordered_pairs = 0
    for i in range(1, len(years)):
        if years[i - 1] >= years[i]:
            ordered_pairs += 1
    denom = max(1, len(years) - 1)
    ratio = ordered_pairs / denom
    score = round(60 * ratio + min(40.0, len(set(years)) * 4.0), 1)
    return max(0.0, min(100.0, score)), f"Fechas coherentes en {ordered_pairs}/{denom} transiciones; años distintos: {len(set(years))}."


def _coverage_score(sections: Dict[str, Any], text: str) -> Tuple[float, str]:
    keys = ["contact", "profile", "experience", "education", "languages", "skills"]
    present = [k for k in keys if sections.get(k)]
    coverage = 100.0 * (len(present) / float(len(keys)))
    # Chequeo simple de contacto
    email = bool(re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text or ""))
    phone = bool(re.search(r"\+?\d[\d\s().-]{7,}", text or ""))
    bonus = 5.0 * sum([email, phone])
    score = max(0.0, min(100.0, round(coverage * 0.9 + bonus, 1)))
    expl = f"Cobertura de secciones {len(present)}/{len(keys)}; contacto: email={email}, teléfono={phone}."
    return score, expl


def _spelling_score(text: str, lang: str) -> Tuple[float, str]:
    if not text or SpellChecker is None:
        return 100.0, "Sin texto o corrector no disponible."
    try:
        lang_code = lang if lang in ("es", "en", "pt") else "es"
        sp = SpellChecker(language=lang_code)
        tokens = [t.lower() for t in re.findall(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ]{3,}", text)]
        if not tokens:
            return 100.0, "Sin tokens."
        miss = sp.unknown(tokens[:5000])
        rate = (len(miss) / float(max(1, len(set(tokens))))) * 1000.0
        score = max(0.0, min(100.0, round(100.0 - min(60.0, rate * 0.6), 1)))
        return score, f"Errores estimados: {rate:.1f} por 1.000 palabras únicas."
    except Exception:
        return 100.0, "Corrector no disponible."


def compute_review_from_text_sections(text: str, sections: Dict[str, Any]) -> Dict[str, Any]:
    """Calcula las 5 métricas a partir de texto y secciones ya extraídas."""
    text = (text or "").strip()
    sections = sections or {}
    # 1) Formato: encabezados presentes + bullets + densidad
    headers = sum(1 for k in ("experience", "education", "profile", "skills", "languages", "contact") if sections.get(k))
    bullets = _bullet_count(text)
    words = len(re.findall(r"\p{L}+", text, flags=re.UNICODE))
    pages_est = max(1.0, len(text) / 2000.0)
    density = words / pages_est
    font_diversity_proxy = 100.0  # sin layout real, no penalizamos por fuentes
    header_score = min(100.0, headers * 15.0)  # hasta ~90
    bullet_bonus = min(20.0, bullets * 0.2)
    density_score = 100.0 - max(0.0, (density - 600.0) * 0.02)  # densidad ideal ~600 palabras/página
    formato = max(0.0, min(100.0, round(0.35 * font_diversity_proxy + 0.35 * header_score + 0.10 * bullet_bonus + 0.20 * density_score, 1)))

    # 2) Claridad: longitud media de frase y ratio de viñetas
    avg_len = _avg_words_per_sentence(text)
    bullet_ratio = (bullets / float(max(1, len(re.split(r"[\.!?]+", text)))))
    claridad = max(0.0, min(100.0, round(100.0 - max(0.0, (avg_len - 22.0) * 3.0) + min(20.0, bullet_ratio * 20.0), 1)))

    # 3) Coherencia: orden temporal aproximado en experiencia
    exp_lines: List[str] = []
    raw_exp = sections.get("experience")
    if isinstance(raw_exp, list):
        exp_lines = [str(x) for x in raw_exp]
    elif isinstance(raw_exp, str):
        exp_lines = raw_exp.splitlines()
    coherencia, coher_expl = _coherence_score_from_experience_lines(exp_lines)

    # 4) Información clave: cobertura de secciones + contacto básico
    info, info_expl = _coverage_score(sections, text)

    # 5) Ortografía
    lang = _detect_language_basic(text)
    spell, spell_expl = _spelling_score(text, lang)

    out = {
        "name": "CVStructureReview",
        "schema": {
            "type": "object"
        },  # decorativo para compatibilidad con response_format opcional
        "strict": True,
        "file_name": "",
        "language": lang,
        "scores": {
            "format": {"score": formato, "stars": stars_from_score(formato), "explanation": f"Encabezados: {headers}; viñetas: {bullets}; densidad ~{int(density)} palabras/página."},
            "clarity": {"score": claridad, "stars": stars_from_score(claridad), "explanation": f"Longitud media de frase: {avg_len:.1f}; ratio viñetas/frases: {bullet_ratio:.2f}."},
            "coherence": {"score": coherencia, "stars": stars_from_score(coherencia), "explanation": coher_expl},
            "key_information": {"score": info, "stars": stars_from_score(info), "explanation": info_expl},
            "spelling": {"score": spell, "stars": stars_from_score(spell), "explanation": spell_expl},
        },
    }
    return out


def analyze_cv_structure(path: str, lang_hint: str = "auto") -> Dict[str, Any]:
    """Analiza un fichero PDF. Si PyMuPDF no está disponible, devuelve un
    resultado neutro para no romper el flujo."""
    text: str = ""
    if fitz is not None:
        try:
            doc = fitz.open(path)  # type: ignore[arg-type]
            parts: List[str] = []
            for p in doc:
                try:
                    parts.append(p.get_text() or "")
                except Exception:
                    continue
            doc.close()
            text = "\n".join(parts)
        except Exception:
            text = ""

    if not text:
        # Devolver un resultado seguro con puntuaciones medias
        lang = "es" if lang_hint == "auto" else lang_hint
        base = {
            "name": "CVStructureReview",
            "schema": {"type": "object"},
            "strict": True,
            "file_name": path.split("/")[-1],
            "language": lang,
            "scores": {
                "format": {"score": 60.0, "stars": 3, "explanation": "No se pudo extraer texto; puntuación por defecto."},
                "clarity": {"score": 60.0, "stars": 3, "explanation": "No se pudo extraer texto; puntuación por defecto."},
                "coherence": {"score": 60.0, "stars": 3, "explanation": "No se pudo extraer texto; puntuación por defecto."},
                "key_information": {"score": 60.0, "stars": 3, "explanation": "No se pudo extraer texto; puntuación por defecto."},
                "spelling": {"score": 60.0, "stars": 3, "explanation": "No se pudo extraer texto; puntuación por defecto."},
            },
        }
        return base

    # Secciones rudimentarias por encabezados, si están en el texto
    sections: Dict[str, Any] = {}
    for key, pat in SECTION_PATTERNS.items():
        if re.search(pat, text, re.IGNORECASE):
            # Extraer un bloque sencillo desde el encabezado hasta el siguiente salto doble
            m = re.search(rf"{pat}.*?(\n\s*\n|$)", text, re.IGNORECASE | re.DOTALL)
            if m:
                sections[key] = m.group(0)
    review = compute_review_from_text_sections(text, sections)
    review["file_name"] = path.split("/")[-1]
    return review


def review_to_ui_diagnostico(review: Dict[str, Any]) -> Dict[str, Any]:
    """Convierte el resultado del analizador al dict esperado por la UI."""
    scores = (review or {}).get("scores", {}) or {}
    fmt = scores.get("format", {}) or {}
    cla = scores.get("clarity", {}) or {}
    coh = scores.get("coherence", {}) or {}
    key = scores.get("key_information", {}) or {}
    spe = scores.get("spelling", {}) or {}
    return {
        "structure_score": int(fmt.get("stars") or 3),
        "coherence_score": int(coh.get("stars") or 3),
        "key_info_score": int(key.get("stars") or 3),
        "clarity_score": int(cla.get("stars") or 3),
        "spelling_style_score": int(spe.get("stars") or 3),
        "evidence": {
            "structure": str(fmt.get("explanation") or ""),
            "coherence": str(coh.get("explanation") or ""),
            "key_info": str(key.get("explanation") or ""),
            "clarity": str(cla.get("explanation") or ""),
            "style": str(spe.get("explanation") or ""),
        },
        "corrections": [],
        "reordering_suggestions": [],
    }


