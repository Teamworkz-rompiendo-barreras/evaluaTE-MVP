import json
import logging
import os
import time
from typing import Any, Dict, List, Optional
from cv_analyzer import extract_text_from_pdf_bytes



try:
    import google.generativeai as genai  # type: ignore
except ImportError:
    try:
        from backend import gemini_lite as genai  # type: ignore
    except ImportError:
        import gemini_lite as genai  # type: ignore

from fastapi import FastAPI, File, Form, HTTPException, Request, Response, UploadFile  # type: ignore
from fastapi.middleware.cors import CORSMiddleware  # type: ignore

# Importaciones locales
try:
    from backend.cv_analyzer import extract_pdf_info, analyze_multimodal_report, analyze_cv_with_ai  # type: ignore
    from backend.prompt_config import PromptConfig  # type: ignore
    from backend.new_report_schema import NewReportSchema, convert_old_format_to_new  # type: ignore
except ImportError:
    from cv_analyzer import extract_pdf_info, analyze_multimodal_report, analyze_cv_with_ai  # type: ignore
    from prompt_config import PromptConfig  # type: ignore
    from new_report_schema import NewReportSchema, convert_old_format_to_new  # type: ignore

# Scoring pipeline (optional — works without it)
_compute_cv_analysis = None
try:
    import sys as _sys, os as _os
    _root = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
    if _root not in _sys.path:
        _sys.path.insert(0, _root)
    from app.cv_pipeline.scoring import compute_cv_analysis as _compute_cv_analysis  # type: ignore
except Exception:
    pass

# Importar servicio PDF
create_employability_pdf = None
try:
    from backend.pdf_service import create_employability_pdf  # type: ignore
except ImportError:
    try:
        from pdf_service import create_employability_pdf  # type: ignore
    except ImportError:
        pass


# Configurar logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configurar Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase_client = None

if SUPABASE_URL and SUPABASE_KEY:
    try:
        from supabase import create_client, Client  # type: ignore
        supabase_client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        logger.info("Supabase client initialized")
    except ImportError:
        logger.warning("Supabase library not found.")
    except Exception as e:
        logger.error(f"Failed to initialize Supabase client: {e}")

# Configurar Gemini
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
if not GOOGLE_API_KEY:
    logger.warning("GOOGLE_API_KEY no está configurada.")
elif genai:
    genai.configure(api_key=GOOGLE_API_KEY)

APP_TITLE = os.getenv("APP_TITLE", "EvaluaTE Backend")
APP_VERSION = "2.1.0 - FormData Fix"

app = FastAPI(title=APP_TITLE, version=APP_VERSION)

# Configuración CORS
allowed_origins_env = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:3000,http://localhost:5173,https://evalua-te-mvp.vercel.app",
)
ALLOWED_ORIGINS = [o.strip() for o in allowed_origins_env.split(",") if o.strip()]

if os.getenv("PRODUCTION", "false").lower() == "true":
    default_domains = ["https://evalua-te-mvp.vercel.app"]
    for dom in default_domains:
        if dom not in ALLOWED_ORIGINS:
            ALLOWED_ORIGINS.append(dom)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health_check():
    return {"status": "ok", "service": "evaluate-backend", "version": APP_VERSION}


# ──────────────────────────────────────────────────────────────────────
# ENDPOINT PRINCIPAL: /api/analyze
# El frontend envía FormData con:
#   - game_results  (JSON string)
#   - preferences   (JSON string)
#   - cv_file       (UploadFile, opcional)
# ──────────────────────────────────────────────────────────────────────
@app.post("/api/analyze")
async def analyze_computational_profile(
    request: Request,
    cv_file: Optional[UploadFile] = File(None),
    game_results: str = Form("{}"),
    preferences: str = Form("{}"),

):
    print("usa api/analyze")

    if cv_file:
        print("cv recibido: ", cv_file.filename)
    else: 
        print("no recibido cv")

    """
    Endpoint principal para generar el informe de empleabilidad.
    Acepta FormData (game_results, preferences, cv_file).
    """
    try:
        user_id = request.headers.get("X-User-Id")

        # 1. Parsear JSON strings del FormData
        try:
            games_data = json.loads(game_results)
        except json.JSONDecodeError:
            games_data = {}
        try:
            prefs_data = json.loads(preferences)
        except json.JSONDecodeError:
            prefs_data = {}

        # 2. Leer y gestionar archivo PDF
        pdf_bytes = None
        cv_text = ""

        if cv_file:
            pdf_bytes = await cv_file.read()

            logger.info("CV recibido:", cv_file.filename)
            logger.info("Tamaño del archivo:", len(pdf_bytes))

            cv_text = extract_text_from_pdf_bytes(pdf_bytes)
            logger.info(f"texto extraido del cv: {cv_text[:500]}")

            # A. Subir CV a Supabase (Backup)
            if pdf_bytes and supabase_client and user_id:
                try:
                    file_ext = cv_file.filename.split(".")[-1] if cv_file.filename else "pdf"
                    file_path = f"{user_id}/{int(time.time())}.{file_ext}"
                    supabase_client.storage.from_("cvs").upload(
                        path=file_path,
                        file=pdf_bytes,
                        file_options={"content-type": cv_file.content_type or "application/pdf"}
                    )
                    logger.info(f"CV uploaded to Supabase: {file_path}")
                except Exception as storage_err:
                    logger.error(f"Supabase upload failed: {storage_err}")

        # 3. Preparar contexto (Juegos y Preferencias)
        employability_score = 75
        level = "medio"
        
        # Normalizar game results
        completed_games_list: list = []
        soft_skills_data: list = []

        if isinstance(games_data, list):
            completed_games_list = [g.get("name", "Juego") for g in games_data]
        elif isinstance(games_data, dict):
            completed_games_list = games_data.get("completedGames", [])
            soft_skills_data = games_data.get("softSkills", [])

        if not soft_skills_data:
            # Fallback soft skills if empty
            soft_skills_data = [
                {"skill": "Resolución de problemas", "score": 80, "level": "alto"},
                {"skill": "Adaptabilidad", "score": 75, "level": "medio"},
                {"skill": "Atención al detalle", "score": 85, "level": "alto"},
            ]

        # 4. Validar API Key
        if not GOOGLE_API_KEY:
            logger.warning("No API Key. Returning mock.")
            return {
                "resumen_ejecutivo": "MOCK MODE (No API Key)",
                "datos_personales": {"nombre": "Mock Candidate"},
                "mensaje_final_azul": "Mock Mode"
            }
            
        if not genai:
             raise HTTPException(500, "Generative AI service not initialized")

        # 5. Generar Informe (Multimodal o Texto)
        analysis_result = {}
        
        if pdf_bytes:
            # MODO MULTIMODAL (Optimizado)
            prompt = PromptConfig.get_employability_report_prompt(
                candidate_data={"fullName": "Candidato"},
                soft_skills_data=soft_skills_data,
                cv_data={}, 
                job_preferences_data=prefs_data,
                employability_score=employability_score,
                level=level,
                completed_games=completed_games_list,
                languages_data=[],
                full_raw_text=cv_text,
                is_multimodal=False
            )


            analysis_result = await analyze_multimodal_report(pdf_bytes, prompt)
            
            if "error" in analysis_result:
                 raise HTTPException(500, detail=analysis_result["error"])
        else:
            # MODO TEXTO (Sin CV)
            prompt = PromptConfig.get_employability_report_prompt(
                candidate_data={"fullName": "Candidato"},
                soft_skills_data=soft_skills_data,
                cv_data={}, 
                job_preferences_data=prefs_data,
                employability_score=employability_score,
                level=level,
                completed_games=completed_games_list,
                languages_data=[],
                is_multimodal=False
            )
            
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = await model.generate_content_async(
                prompt, 
                generation_config=genai.types.GenerationConfig(response_mime_type="application/json")
            )
            # Parsear respuesta manual (o usar helper si estuviéramos en cv_analyzer)
            try:
                analysis_result = json.loads(response.text)
            except:
                # Cleanup simple json markdown
                txt = response.text.replace("```json", "").replace("```", "").strip()
                analysis_result = json.loads(txt)

        # 7. Persistir en Supabase
        if supabase_client and user_id:
            try:
                report_payload = {
                    "user_id": user_id,
                    "employability_score": employability_score,
                    "level": str(level),
                    "report_json": analysis_result,
                    "created_at": "now()",
                }
                supabase_client.table("employability_reports").insert(
                    report_payload
                ).execute()
                logger.info(f"Report saved to Supabase for user {user_id}")
            except Exception as db_err:
                logger.error(f"Error saving to Supabase: {db_err}")

        return analysis_result

    except Exception as e:
        logger.exception("Error en /api/analyze")
        raise HTTPException(status_code=500, detail=str(e))


#test

@app.get("/api/test-main")
async def test_main():
    return {"ok": True, "message": "main activo"}

@app.post("/api/test-post")
async def test_post(data: dict):
    return {
        "ok": True,
        "message": "POST funcionando correctamente",
        "data": data
    }


# ──────────────────────────────────────────────────────────────────────
# ENDPOINT DE GENERACIÓN DE PDF
# ──────────────────────────────────────────────────────────────────────
@app.post("/api/report/generate")
async def generate_pdf_report(
    report_data: dict, filename: Optional[str] = "reporte_empleabilidad.pdf"
):
    """Genera el PDF a partir del JSON del informe."""
    try:
        if not create_employability_pdf:
            raise HTTPException(
                status_code=500, detail="PDF Service not available (reportlab missing)"
            )
        #convierte al formato correcto y los valida para usarlos en pdf_service.py
        try:
            converted_data = convert_old_format_to_new(report_data)
            report_schema = NewReportSchema(**converted_data)
        except Exception as val_err:
            logger.error(f"Schema Validation Failed: {val_err}")
            raise HTTPException(
                status_code=400, detail=f"Invalid JSON Schema: {val_err}"
            )

        pdf_bytes = create_employability_pdf(report_schema)

        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error generando PDF")
        raise HTTPException(status_code=500, detail=str(e))


# ──────────────────────────────────────────────────────────────────────
# ENDPOINT DE DEBUG CV
# El frontend auto-analyze envía FormData con solo un campo 'file'
# ──────────────────────────────────────────────────────────────────────
@app.post("/api/debug/cv_data")
async def api_debug_cv_data(file: UploadFile = File(...)) -> Dict[str, Any]:
    """Return the raw CV extraction JSON for debugging purposes."""
    try:
        pdf_bytes = await file.read()
        if not pdf_bytes:
            raise HTTPException(status_code=400, detail="Archivo vacío")
        result = await extract_pdf_info(pdf_bytes)
        return result
    except Exception as e:
        logger.exception("Error in debug endpoint")
        raise HTTPException(status_code=500, detail=f"Error debug CV: {e}")


# ──────────────────────────────────────────────────────────────────────
# FEEDBACK DE INFORME IA
# ──────────────────────────────────────────────────────────────────────

import smtplib
import datetime
import uuid as uuid_lib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

FEEDBACK_SMTP_HOST = os.getenv("SMTP_HOST", "")
FEEDBACK_SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
FEEDBACK_SMTP_USER = os.getenv("SMTP_USER", "")
FEEDBACK_SMTP_PASS = os.getenv("SMTP_PASSWORD", "")
FEEDBACK_FROM     = os.getenv("FROM_EMAIL", FEEDBACK_SMTP_USER)
FEEDBACK_TO       = os.getenv("FEEDBACK_EMAIL", "rural.minds@teamworkz.co")


def _send_feedback_email(data: dict) -> None:
    if not (FEEDBACK_SMTP_HOST and FEEDBACK_SMTP_USER and FEEDBACK_SMTP_PASS):
        return
    try:
        rating_icon = "👍" if data.get("rating") == "Útil" else "👎"
        msg = MIMEMultipart()
        msg["From"]    = FEEDBACK_FROM
        msg["To"]      = FEEDBACK_TO
        msg["Subject"] = f"[evaluaTE] Nuevo feedback: {data.get('rating', '?')}"
        body = f"""
        <html><body style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto">
        <h2>{rating_icon} Nuevo feedback en evaluaTE</h2>
        <p><strong>Valoración:</strong> {data.get('rating', '?')}</p>
        <p><strong>Comentario:</strong> {data.get('comment') or '(sin comentario)'}</p>
        <p><strong>Fecha:</strong> {data.get('timestamp', '')}</p>
        </body></html>
        """
        msg.attach(MIMEText(body, "html"))
        with smtplib.SMTP(FEEDBACK_SMTP_HOST, FEEDBACK_SMTP_PORT) as s:
            s.ehlo(); s.starttls(); s.ehlo()
            s.login(FEEDBACK_SMTP_USER, FEEDBACK_SMTP_PASS)
            s.sendmail(FEEDBACK_FROM, [FEEDBACK_TO], msg.as_string())
        logger.info(f"Feedback email sent to {FEEDBACK_TO}")
    except Exception as e:
        logger.error(f"Error sending feedback email: {e}")


import asyncio as _asyncio

@app.post("/api/pdf/analyze-cv")
async def analyze_cv_endpoint(cv_file: UploadFile = File(...)):
    """
    Dedicated CV analysis endpoint.
    Extracts structure, contact, experience, education from PDF via Gemini
    and returns CvAnalysis format expected by the frontend.
    """
    try:
        pdf_bytes = await cv_file.read()
        if not pdf_bytes:
            raise HTTPException(status_code=400, detail="Empty file")

        # Extract CV data via Gemini (uses gemini_lite inline data on Vercel)
        cv_data = await _asyncio.to_thread(analyze_cv_with_ai, pdf_bytes)

        if isinstance(cv_data, dict) and "error" in cv_data:
            raise HTTPException(status_code=500, detail=cv_data["error"])

        dp = cv_data.get("datos_personales") or {}
        experiencia = cv_data.get("experiencia") or []
        educacion = cv_data.get("educacion") or []
        idiomas = cv_data.get("idiomas") or []
        habilidades = cv_data.get("habilidades_detectadas") or []
        resumen = cv_data.get("resumen_profesional") or ""

        contact = {
            "name": dp.get("nombre", ""),
            "emails": [dp["email"]] if dp.get("email") else [],
            "phones": [dp["telefono"]] if dp.get("telefono") else [],
            "location": dp.get("ubicacion", ""),
            "linkedin": dp.get("linkedin", ""),
        }

        # Compute structure scores
        if _compute_cv_analysis:
            cv_normalized = {
                "experience": experiencia,
                "education": educacion,
                "languages": idiomas,
                "skills": [h.get("herramienta", "") for h in habilidades if h.get("herramienta")],
                "contact": {
                    "emails": contact["emails"],
                    "phones": contact["phones"],
                    "location": contact["location"],
                    "linkedin": contact["linkedin"],
                },
                "summary": bool(resumen),
                "sections": len(experiencia) > 0,
            }
            scored = _compute_cv_analysis(cv_normalized)
            dim = {d["id"]: d["score"] for d in scored.get("dimensions", [])}
            # Map pipeline dimensions (1-5) to frontend score (0-100)
            structure_score = dim.get("structure", 3) * 20
            coherence_score = dim.get("experience", 3) * 20
            key_info_score  = dim.get("contact", 3) * 20
            clarity_score   = dim.get("education", 3) * 20
            style_score     = dim.get("tools", 3) * 20
        else:
            # Heuristic fallback when scoring module unavailable
            structure_score = 60 if resumen else 40
            coherence_score = min(100, len(experiencia) * 20) or 40
            key_info_score  = (60 if contact["emails"] else 0) + (20 if contact["phones"] else 0) + (20 if contact["location"] else 0)
            clarity_score   = min(100, len(educacion) * 25) or 40
            style_score     = min(100, len(habilidades) * 10) or 40

        corrections = []
        if not contact["emails"]:
            corrections.append("Añade un email de contacto")
        if not contact["phones"]:
            corrections.append("Añade un teléfono de contacto")
        if not resumen:
            corrections.append("Añade un resumen/perfil profesional")
        if not educacion:
            corrections.append("Añade tu formación académica")

        return {
            "structure_score": structure_score,
            "coherence_score": coherence_score,
            "key_info_score": key_info_score,
            "clarity_score": clarity_score,
            "style_score": style_score,
            "evidence": {
                "structure": f"Secciones detectadas: experiencia, educación, habilidades{'  resumen' if resumen else ''}",
                "coherence": f"{len(experiencia)} experiencia(s) laboral(es) detectada(s)",
                "key_info": f"Contacto: {'email ✓' if contact['emails'] else 'email ✗'} · {'teléfono ✓' if contact['phones'] else 'teléfono ✗'} · {'ubicación ✓' if contact['location'] else 'ubicación ✗'}",
                "clarity": f"{len(educacion)} formación(es) académica(s) detectada(s)",
                "style": f"{len(habilidades)} herramienta(s)/habilidad(es) detectada(s)",
            },
            "corrections": corrections,
            "reordering_suggestions": [],
            "experience_detailed": experiencia,
            "education_detailed": educacion,
            "languages": idiomas,
            "software": [{"name": h.get("herramienta"), "level": h.get("nivel")} for h in habilidades],
            "contact": contact,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error en /api/pdf/analyze-cv")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/informe-ia/feedback")
async def submit_feedback(request: Request):
    """Recibe el feedback del usuario sobre el informe de IA."""
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="JSON inválido")

    timestamp = datetime.datetime.utcnow().isoformat()
    record = {
        "id": str(uuid_lib.uuid4()),
        "rating": body.get("rating", ""),
        "comment": body.get("comment", ""),
        "timestamp": timestamp,
        "user_data": body.get("userData", {}),
    }

    # Guardar en Supabase
    if supabase_client:
        try:
            supabase_client.table("feedback_ia").insert(record).execute()
            logger.info(f"Feedback saved to Supabase: {record['id']}")
        except Exception as e:
            logger.error(f"Supabase insert failed (table may not exist): {e}")

    # Notificar por email
    _send_feedback_email(record)

    logger.info(f"Feedback received: rating={record['rating']}")
    return {"ok": True, "id": record["id"]}


@app.get("/api/informe-ia/feedback/stats")
async def feedback_stats():
    """Devuelve estadísticas de feedback para el dashboard."""
    if not supabase_client:
        return {
            "total_feedback": 0,
            "useful_feedback": 0,
            "not_useful_feedback": 0,
            "satisfaction_rate": 0,
            "recent_feedback": [],
        }
    try:
        res = supabase_client.table("feedback_ia").select("*").order("timestamp", desc=True).limit(100).execute()
        rows = res.data or []
        useful     = [r for r in rows if r.get("rating") == "Útil"]
        not_useful = [r for r in rows if r.get("rating") != "Útil"]
        total      = len(rows)
        return {
            "total_feedback": total,
            "useful_feedback": len(useful),
            "not_useful_feedback": len(not_useful),
            "satisfaction_rate": round(len(useful) / total * 100, 1) if total else 0,
            "recent_feedback": rows[:20],
        }
    except Exception as e:
        logger.error(f"Error fetching feedback stats: {e}")
        return {
            "total_feedback": 0,
            "useful_feedback": 0,
            "not_useful_feedback": 0,
            "satisfaction_rate": 0,
            "recent_feedback": [],
        }


if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8080"))
    import uvicorn  # type: ignore

    uvicorn.run("main:app", host=host, port=port, reload=False)
