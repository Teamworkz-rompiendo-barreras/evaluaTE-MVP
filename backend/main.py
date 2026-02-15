import json
import logging
import os
import time
from typing import Any, Dict, List, Optional

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
    from backend.cv_analyzer import extract_pdf_info  # type: ignore
    from backend.prompt_config import PromptConfig  # type: ignore
    from backend.new_report_schema import NewReportSchema  # type: ignore
except ImportError:
    from cv_analyzer import extract_pdf_info  # type: ignore
    from prompt_config import PromptConfig  # type: ignore
    from new_report_schema import NewReportSchema  # type: ignore

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

        # 2. Leer y analizar CV (si existe)
        cv_data: Dict[str, Any] = {}
        full_text = ""

        if cv_file:
            pdf_bytes = await cv_file.read()
            if pdf_bytes:
                # A. Subir CV a Supabase Storage
                if supabase_client and user_id:
                    try:
                        file_ext = "pdf"
                        if cv_file.filename:
                            parts = cv_file.filename.split(".")
                            if len(parts) > 1:
                                file_ext = parts[-1]
                        file_path = f"{user_id}/{int(time.time())}.{file_ext}"
                        supabase_client.storage.from_("cvs").upload(
                            path=file_path,
                            file=pdf_bytes,
                            file_options={
                                "content-type": cv_file.content_type or "application/pdf"
                            },
                        )
                        logger.info(f"CV uploaded to Supabase: {file_path}")
                    except Exception as storage_err:
                        logger.error(f"Failed to upload CV to Supabase: {storage_err}")

                # B. Analizar CV con Gemini
                cv_extraction = await extract_pdf_info(pdf_bytes)
                if cv_extraction:
                    cv_data = cv_extraction.get("cv_info", {})
                    full_text = cv_extraction.get("raw_text", "")

        # 3. Preparar datos para el prompt
        candidate_name = cv_data.get("datos_personales", {}).get("nombre", "Candidato")

        employability_score = 75
        level = "medio"

        # Normalizar game results
        completed_games_list: list = []
        soft_skills_data: list = []

        if isinstance(games_data, list):
            completed_games_list = [
                g.get("name", "Juego desconocido") for g in games_data
            ]
        elif isinstance(games_data, dict):
            completed_games_list = games_data.get("completedGames", [])
            soft_skills_data = games_data.get("softSkills", [])

        if not soft_skills_data:
            soft_skills_data = [
                {"skill": "Resolución de problemas", "score": 80, "level": "alto"},
                {"skill": "Adaptabilidad", "score": 75, "level": "medio"},
                {"skill": "Atención al detalle", "score": 85, "level": "alto"},
            ]

        # 4. Generar Prompt
        prompt = PromptConfig.get_employability_report_prompt(
            candidate_data={"fullName": candidate_name},
            soft_skills_data=soft_skills_data,
            cv_data=cv_data,
            job_preferences_data=prefs_data,
            employability_score=employability_score,
            level=level,
            completed_games=completed_games_list,
            languages_data=cv_data.get("idiomas", []),
            full_raw_text=full_text,
        )

        # 5. Llamar a Gemini
        if not GOOGLE_API_KEY:
            logger.warning("API Key no configurada, retornando mock data")
            return {
                "resumen_ejecutivo": "MOCK: No API Key configured.",
                "datos_personales": {
                    "nombre": candidate_name,
                    "ubicacion": "Madrid",
                    "email": "mock@email.com",
                    "phone": "000000000",
                },
                "mensaje_final_azul": "Mock Mode",
            }

        if not genai:
            raise HTTPException(
                status_code=500, detail="Generative AI library not available"
            )

        model = genai.GenerativeModel("gemini-1.5-flash")
        generation_config = genai.types.GenerationConfig(
            response_mime_type="application/json"
        )

        logger.info("Sending prompt to Gemini...")
        response = await model.generate_content_async(
            prompt, generation_config=generation_config
        )

        response_text = response.text

        # 6. Parsear respuesta
        try:
            analysis_result = json.loads(response_text)
        except json.JSONDecodeError:
            msg = response_text
            if "```json" in msg:
                msg = msg.split("```json")[1].split("```")[0]
            elif "```" in msg:
                msg = msg.split("```")[1].split("```")[0]
            analysis_result = json.loads(msg.strip())

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

        try:
            report_schema = NewReportSchema(**report_data)
        except Exception as val_err:
            logger.error(f"Schema Validation Failed: {val_err}")
            raise HTTPException(
                status_code=400, detail=f"Invalid JSON Schema: {val_err}"
            )

        pdf_bytes = create_employability_pdf(report_schema)

        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"},
        )
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


if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8080"))
    import uvicorn  # type: ignore

    uvicorn.run("main:app", host=host, port=port, reload=False)
