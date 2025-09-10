# -*- coding: utf-8 -*-
"""
EvaluaTE Backend - FastAPI entrypoint
- GET /health
- POST /api/informe-ia
- POST /api/pdf/generate-report
"""

import os
import logging
from typing import Any, Dict

from fastapi import FastAPI, HTTPException, Request, Response, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware

# Import robusto compatible tanto si se ejecuta como paquete (backend.main)
# como si se ejecuta directamente desde el directorio backend
try:
    from backend.generate_report import generar_informe
    from backend.pdf_service import create_employability_pdf
    from backend.cv_analyzer import extract_pdf_info
except ImportError:  # fallback a imports relativos al directorio actual
    from generate_report import generar_informe
    from pdf_service import create_employability_pdf
    from cv_analyzer import extract_pdf_info

APP_TITLE = os.getenv("APP_TITLE", "EvaluaTE Backend")
APP_VERSION = os.getenv("APP_VERSION", "1.0.0")

logger = logging.getLogger("evaluador-backend")

app = FastAPI(title=APP_TITLE, version=APP_VERSION)

# CORS configuration
allowed_origins_env = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:3005,http://localhost:3006,http://localhost:5173,http://localhost:8080,https://evaluador-frontend-fzbhemgtetfeeme6.spaincentral-01.azurestaticapps.net",
)
ALLOWED_ORIGINS = [o.strip() for o in allowed_origins_env.split(",") if o.strip()]

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
            raise HTTPException(status_code=400, detail="Archivo vacío")
        result = extract_pdf_info(pdf_bytes)
        if result.get("error"):
            logger.warning("Fallo en análisis de '%s': %s", file.filename, result.get("error"))
            raise HTTPException(status_code=400, detail=result["error"])
        logger.info("Análisis de '%s' completado", file.filename)

        # Normalizar al shape esperado por el frontend (CvAnalysis)
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
            "ai_analysis": result.get("full_cv_data") or {},
            "cv_analysis_structured": analysis,
        }

        return normalized
    except HTTPException as e:
        logger.warning("Error de cliente al analizar '%s': %s", getattr(file, "filename", "desconocido"), getattr(e, "detail", ""))
        raise
    except Exception as e:
        logger.exception("Error inesperado al analizar '%s'", getattr(file, "filename", "desconocido"))
        raise HTTPException(status_code=500, detail=f"Error analizando CV: {e}")


if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8080"))
    # Lazy import to avoid uvicorn dependency at import time
    import uvicorn

    uvicorn.run("main:app", host=host, port=port, reload=False)


