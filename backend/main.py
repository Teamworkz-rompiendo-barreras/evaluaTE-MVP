# -*- coding: utf-8 -*-
"""
EvaluaTE Backend - FastAPI entrypoint
- GET /health
- POST /api/informe-ia
- POST /api/pdf/generate-report
"""

import os
import json
import logging
from datetime import datetime
from typing import Any, Dict, List

from fastapi import FastAPI, HTTPException, Request, Response, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import robusto compatible tanto si se ejecuta como paquete (backend.main)
# como si se ejecuta directamente desde el directorio backend
try:
    from backend.generate_report import generar_informe
    from backend.pdf_service import create_employability_pdf
    from backend.cv_analyzer import extract_pdf_info
    from backend.feedback_notifications import feedback_notifier
except ImportError:  # fallback a imports relativos al directorio actual
    from generate_report import generar_informe
    from pdf_service import create_employability_pdf
    from cv_analyzer import extract_pdf_info
    from feedback_notifications import feedback_notifier


FEEDBACK_STORE = os.getenv("FEEDBACK_FILE", os.path.join(os.getcwd(), "feedback_ia.json"))

APP_TITLE = os.getenv("APP_TITLE", "EvaluaTE Backend")
APP_VERSION = os.getenv("APP_VERSION", "1.0.0")

app = FastAPI(title=APP_TITLE, version=APP_VERSION)

# CORS configuration
allowed_origins_env = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:3005,http://localhost:3006,http://localhost:5173,http://localhost:8080,https://evaluador-frontend-fzbhemgtetfeeme6.spaincentral-01.azurestaticapps.net",
)
ALLOWED_ORIGINS = [o.strip() for o in allowed_origins_env.split(",") if o.strip()]

# Permitir por regex cualquier dominio de Azure Static Web Apps
# Ejemplo: https://<random>.<zone>.azurestaticapps.net
ALLOW_ORIGIN_REGEX = os.getenv(
    "ALLOW_ORIGIN_REGEX",
    r"https://.*\\.azurestaticapps\\.net$",
)

# En producción, permitir también dominios de Azure Static Web Apps
if os.getenv("PRODUCTION", "false").lower() == "true":
    # Agregar dominios de Azure Static Web Apps si no están ya incluidos
    azure_domains = [
        "https://evaluador-frontend-fzbhemgtetfeeme6.spaincentral-01.azurestaticapps.net",
        "https://*.azurestaticapps.net",  # Patrón para cualquier Azure Static Web App
    ]
    for domain in azure_domains:
        if domain not in ALLOWED_ORIGINS:
            ALLOWED_ORIGINS.append(domain)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS or ["*"],
    allow_origin_regex=ALLOW_ORIGIN_REGEX,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root() -> Dict[str, Any]:
    return {"name": APP_TITLE, "version": APP_VERSION}


@app.get("/health")
def health() -> Dict[str, Any]:
    return {"status": "ok"}


def _load_feedback() -> List[Dict[str, Any]]:
    try:
        if os.path.exists(FEEDBACK_STORE):
            with open(FEEDBACK_STORE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    return data
    except Exception:
        logger.exception("No se pudo leer el fichero de feedback")
    return []


def _save_feedback(entries: List[Dict[str, Any]]) -> None:
    try:
        with open(FEEDBACK_STORE, "w", encoding="utf-8") as f:
            json.dump(entries, f, ensure_ascii=False, indent=2)
    except Exception:
        logger.exception("No se pudo guardar el fichero de feedback")


@app.post("/api/informe-ia")
async def api_informe_ia(req: Request) -> Dict[str, Any]:
    try:
        payload: Dict[str, Any] = await req.json()
    except Exception:
        raise HTTPException(status_code=400, detail="JSON inválido")

    if not isinstance(payload, dict):
        raise HTTPException(status_code=400, detail="Payload debe ser un objeto JSON")

    # Generar informe determinista usando la lógica local
    try:
        result = generar_informe(payload)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando informe: {e}")

    # Asegurar forma compatible para el frontend actual
    if not isinstance(result, dict):
        raise HTTPException(status_code=500, detail="Respuesta inválida del generador")

    return result


@app.post("/api/informe-ia/feedback")
async def api_feedback(req: Request) -> Dict[str, Any]:
    try:
        payload: Dict[str, Any] = await req.json()
    except Exception:
        raise HTTPException(status_code=400, detail="JSON inválido")

    feedback_entries = _load_feedback()
    entry = {
        "rating": payload.get("rating"),
        "comment": payload.get("comment") or "",
        "informe": payload.get("informe") or "",
        "userData": payload.get("userData") or {},
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }
    feedback_entries.append(entry)
    _save_feedback(feedback_entries)

    try:
        feedback_notifier.send_feedback_notification(entry)
    except Exception:
        logger.exception("No se pudo enviar la notificación de feedback")

    return {"status": "ok"}


@app.get("/api/informe-ia/feedback/stats")
def api_feedback_stats() -> Dict[str, Any]:
    feedback_entries = _load_feedback()
    useful = len([f for f in feedback_entries if str(f.get("rating")) == "Útil"])
    not_useful = len([f for f in feedback_entries if str(f.get("rating")) == "No útil"])
    return {
        "total": len(feedback_entries),
        "useful": useful,
        "not_useful": not_useful,
    }


@app.post("/api/report/feedback")
async def api_report_feedback(req: Request) -> Dict[str, Any]:
    try:
        payload: Dict[str, Any] = await req.json()
    except Exception:
        raise HTTPException(status_code=400, detail="JSON inválido")

    feedback_entries = _load_feedback()
    entry = {
        "rating": payload.get("rating"),
        "userId": payload.get("userId"),
        "reportId": payload.get("reportId"),
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }
    feedback_entries.append(entry)
    _save_feedback(feedback_entries)

    return {"status": "ok", "rating": entry.get("rating")}


@app.post("/api/pdf/generate-report")
async def api_pdf_generate(req: Request) -> Response:
    try:
        payload: Dict[str, Any] = await req.json()
    except Exception:
        raise HTTPException(status_code=400, detail="JSON inválido")

    try:
        pdf_bytes = create_employability_pdf(payload)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando PDF: {e}")

    return Response(content=pdf_bytes, media_type="application/pdf")


@app.post("/api/pdf/analyze-cv")
async def api_analyze_cv(file: UploadFile = File(...)) -> Dict[str, Any]:
    try:
        pdf_bytes = await file.read()
        size = len(pdf_bytes) if pdf_bytes else 0
        logger.info("Recibido archivo '%s' (%d bytes)", file.filename, size)
        if not pdf_bytes:
            logger.warning("Archivo vacío recibido")
            raise HTTPException(status_code=400, detail="Archivo vacío")
        try:
            result = extract_pdf_info(pdf_bytes)
            logger.info("extract_pdf_info ejecutado correctamente")
        except Exception as e:
            logger.exception("Fallo ejecutando extract_pdf_info")
            raise HTTPException(status_code=500, detail=f"Error analizando CV: {e}")
        if result.get("error"):
            logger.error("extract_pdf_info devolvió error: %s", result["error"])
            raise HTTPException(status_code=400, detail=result["error"])

        # Normalizar al shape esperado por el frontend (CvAnalysis)
        di_used = bool(result.get("document_intelligence_used"))

        # Dos formatos de entrada posibles:
        # 1) Tradicional: {cv_info: {contacto, educacion, experiencia, idiomas, software, perfil}, analysis: {...}, raw_text}
        # 2) Document Intelligence: {contact, experience, education, languages, software, raw_text, stars, ...}

        if di_used or ("contact" in result or "experience" in result or "education" in result):
            # Mapear salida de Document Intelligence a forma cv_info/analysis
            contact_di: Dict[str, Any] = result.get("contact") or {}
            emails = contact_di.get("emails") or []
            phones = contact_di.get("phones") or []
            location = contact_di.get("location") or ""
            linkedin = contact_di.get("linkedin") or ""
            raw_text = result.get("raw_text") or result.get("raw_text_excerpt") or ""

            lang_items: list = []
            for item in (result.get("languages") or []):
                if isinstance(item, dict):
                    lang_items.append({
                        "name": item.get("language") or item.get("name"),
                        "level": item.get("level") or item.get("nivel") or ""
                    })
                elif isinstance(item, str):
                    lang_items.append({"name": item, "level": ""})

            # Fallbacks: si DI no entregó listas, usar texto raw para no dejar vacío
            exp_fallback = result.get("experience") or []
            edu_fallback = result.get("education") or []
            lang_fallback = lang_items
            sw_fallback = result.get("software") or []
            if raw_text and (not exp_fallback):
                exp_fallback = [raw_text[:400]]
            if raw_text and (not edu_fallback):
                edu_fallback = [raw_text[:400]]
            if raw_text and (not lang_fallback):
                lang_fallback = [{"name": "Idioma no detectado", "level": ""}]
            if raw_text and (not sw_fallback):
                sw_fallback = [raw_text[:200]]

            def _extract_tools_from_text(text: str) -> List[str]:
                """Detecta herramientas conocidas dentro del texto plano del CV."""
                if not text:
                    return []
                catalog = [
                    "microsoft office",
                    "office",
                    "excel",
                    "word",
                    "powerpoint",
                    "outlook",
                    "teams",
                    "photoshop",
                    "illustrator",
                    "indesign",
                    "after effects",
                    "lightroom",
                    "figma",
                    "miro",
                    "notion",
                    "trello",
                    "jira",
                    "asana",
                    "slack",
                ]
                lowered = text.lower()
                found: List[str] = []
                for tool in catalog:
                    if tool in lowered:
                        found.append(tool.title())
                # Orden estable y sin duplicados
                seen = set()
                unique = []
                for item in found:
                    if item not in seen:
                        seen.add(item)
                        unique.append(item)
                return unique

            # Si Document Intelligence devolvió herramientas irrelevantes o vacías,
            # reforzar con extracción simple desde el texto crudo.
            if raw_text:
                tools_from_text = _extract_tools_from_text(raw_text)
                # Reemplazar si no hay herramientas o si solo hay dos genéricas
                if (not sw_fallback) or (len(sw_fallback) <= 2):
                    sw_fallback = tools_from_text or sw_fallback
                else:
                    # Combinar manteniendo prioridad a lo ya extraído
                    combined = list(sw_fallback) + [t for t in tools_from_text if t not in sw_fallback]
                    sw_fallback = combined

            def _stringify_list(items: Any) -> List[str]:
                lines: List[str] = []
                if not items:
                    return lines
                for it in items:
                    if it is None:
                        continue
                    if isinstance(it, dict):
                        parts: List[str] = []
                        for k in (
                            "title",
                            "cargo",
                            "position",
                            "role",
                            "puesto",
                            "company",
                            "empresa",
                            "organization",
                            "organizacion",
                            "period",
                            "duration",
                            "start_date",
                            "fecha_inicio",
                            "end_date",
                            "fecha_fin",
                            "description",
                            "descripcion",
                        ):
                            v = it.get(k)
                            if v:
                                parts.append(str(v))
                        line = " — ".join(parts).strip() if parts else str(it)
                        if line:
                            lines.append(line)
                    else:
                        lines.append(str(it))
                return lines

            normalized: Dict[str, Any] = {
                "strengths": result.get("strengths") or [],
                "weaknesses": result.get("weaknesses") or [],
                "feedback": result.get("feedback") or "",
                "structure": "regular",
                "coherence": "regular",
                "experience": "regular",
                "skills": sw_fallback or [],
                "education": [
                    (e.get("degree") or e.get("titulo") or e.get("title") or "").strip()
                    for e in (edu_fallback or []) if isinstance(e, dict)
                ],
                "alerts": [],
                "cv_structured": {
                    "candidate": contact_di.get("name") or contact_di.get("nombre") or "",
                    "contact": {
                        "emails": emails if isinstance(emails, list) else ([emails] if emails else []),
                        "phones": phones if isinstance(phones, list) else ([phones] if phones else []),
                        "location": location,
                        "linkedin": linkedin,
                    },
                    "experience": exp_fallback or [],
                    "education": edu_fallback or [],
                    "languages": lang_fallback or [],
                    "skills": sw_fallback or [],
                    "summary": result.get("summary") or "",
                },
                "candidate": contact_di.get("name") or contact_di.get("nombre") or "",
                "contact": {
                    "emails": emails if isinstance(emails, list) else ([emails] if emails else []),
                    "phones": phones if isinstance(phones, list) else ([phones] if phones else []),
                    "location": location,
                    "linkedin": linkedin,
                },
                "experience_detailed": exp_fallback or [],
                "education_detailed": edu_fallback or [],
                "languages": lang_fallback or [],
                "software": sw_fallback or [],
                "raw_text": raw_text or "",
                "cv_details": {
                    "experience": _stringify_list(exp_fallback),
                    "education": _stringify_list(edu_fallback),
                    "languages": _stringify_list(lang_fallback),
                    "tools": _stringify_list(sw_fallback),
                },
                "ai_analysis": {},
                "cv_analysis_structured": {"stars": result.get("stars") or {}},
                "document_intelligence_used": True,
            }
            logger.info("CV analysis normalizado correctamente (Document Intelligence)")
            return normalized

        # Formato tradicional
        cv_info: Dict[str, Any] = result.get("cv_info") or {}
        analysis: Dict[str, Any] = result.get("analysis") or {}
        contacto: Dict[str, Any] = cv_info.get("contacto") or {}

        # Contacto → CvContact
        emails = contacto.get("email")
        emails = [emails] if isinstance(emails, str) and emails else (emails if isinstance(emails, list) else [])
        phones = contacto.get("telefono") or contacto.get("phone")
        phones = [phones] if isinstance(phones, str) and phones else (phones if isinstance(phones, list) else [])
        location = contacto.get("ubicacion") or contacto.get("location") or ""
        linkedin = contacto.get("linkedin") or ""

        # Idiomas → lista de objetos {name/level}
        lang_items: list = []
        for item in (cv_info.get("idiomas") or []):
            if isinstance(item, str):
                name, lvl = item, ""
                if "(" in item and ")" in item:
                    try:
                        name = item.split("(")[0].strip()
                        lvl = item.split("(")[1].split(")")[0].strip()
                    except Exception:
                        pass
                lang_items.append({"name": name, "level": lvl})
            elif isinstance(item, dict):
                lang_items.append({
                    "name": item.get("idioma") or item.get("name"),
                    "level": item.get("nivel") or item.get("level")
                })

        normalized: Dict[str, Any] = {
            # Campos básicos
            "strengths": analysis.get("strengths") or [],
            "weaknesses": analysis.get("weaknesses") or [],
            "feedback": analysis.get("feedback") or "",
            "structure": analysis.get("structure") or "regular",
            "coherence": analysis.get("coherence") or "regular",
            "experience": analysis.get("experience") or "regular",
            "skills": cv_info.get("software") or analysis.get("skills") or [],
            "education": [
                (e.get("titulo") or e.get("degree") or e.get("title") or "").strip()
                for e in (cv_info.get("educacion") or []) if isinstance(e, dict)
            ],
            "alerts": analysis.get("alerts") or [],

            # Datos estructurados
            "cv_structured": {
                "candidate": contacto.get("nombre") or "",
                "contact": {
                    "emails": emails,
                    "phones": phones,
                    "location": location,
                    "linkedin": linkedin,
                },
                "experience": cv_info.get("experiencia") or [],
                "education": cv_info.get("educacion") or [],
                "languages": lang_items,
                "skills": cv_info.get("software") or [],
                "summary": cv_info.get("perfil") or "",
            },

            # Campos directos
            "candidate": contacto.get("nombre") or "",
            "contact": {"emails": emails, "phones": phones, "location": location, "linkedin": linkedin},
            "experience_detailed": cv_info.get("experiencia") or [],
            "education_detailed": cv_info.get("educacion") or [],
            "languages": lang_items,
            "raw_text": result.get("raw_text") or "",
            "cv_details": {
                "experience": [
                    " — ".join(
                        part
                        for part in (
                            e.get("titulo") or e.get("degree") or e.get("title") or "",
                            e.get("empresa") or e.get("company") or "",
                            e.get("fecha_inicio") or e.get("start_date") or "",
                            e.get("fecha_fin") or e.get("end_date") or "",
                        )
                        if part
                    ).strip()
                    for e in (cv_info.get("experiencia") or []) if isinstance(e, dict)
                ],
                "education": [
                    " — ".join(
                        part
                        for part in (
                            e.get("titulo") or e.get("degree") or e.get("title") or "",
                            e.get("institucion") or e.get("institution") or e.get("school") or "",
                            e.get("fecha_inicio") or e.get("start_date") or "",
                            e.get("fecha_fin") or e.get("end_date") or "",
                        )
                        if part
                    ).strip()
                    for e in (cv_info.get("educacion") or []) if isinstance(e, dict)
                ],
                "languages": [
                    f"{lang.get('idioma') or lang.get('name') or lang.get('language') or ''} — {lang.get('nivel') or lang.get('level') or ''}".strip(" —")
                    for lang in lang_items
                ],
                "tools": [
                    f"{tool.get('herramienta') or tool.get('name') or tool.get('tool') or ''} — {tool.get('nivel') or tool.get('level') or ''}".strip(" —")
                    for tool in (cv_info.get("software") or [])
                    if isinstance(tool, dict)
                ],
            },
            "ai_analysis": result.get("full_cv_data") or {},
            "cv_analysis_structured": analysis,
            "document_intelligence_used": False,
        }
        logger.info("CV analysis normalizado correctamente")
        return normalized
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error inesperado en api_analyze_cv")
        raise HTTPException(status_code=500, detail=f"Error analizando CV: {e}")


if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8080"))
    # Lazy import to avoid uvicorn dependency at import time
    import uvicorn

    uvicorn.run("main:app", host=host, port=port, reload=False)


