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
    from backend.cv_analyzer import extract_pdf_info, analyze_multimodal_report  # type: ignore
    from backend.prompt_config import PromptConfig  # type: ignore
    from backend.new_report_schema import NewReportSchema, convert_old_format_to_new  # type: ignore
except ImportError:
    from cv_analyzer import extract_pdf_info, analyze_multimodal_report  # type: ignore
    from prompt_config import PromptConfig  # type: ignore
    from new_report_schema import NewReportSchema, convert_old_format_to_new  # type: ignore

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

        # 2. Leer y gestionar archivo PDF
        pdf_bytes = None
        if cv_file:
            pdf_bytes = await cv_file.read()
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
                is_multimodal=True
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
# ENDPOINT CONEXION FEEDBACK
# ──────────────────────────────────────────────────────────────────────
@app.post("/api/informe-ia/feedback")
async def receive_feedback(feedback_data: dict):
    try:
        logger.info(f"feedback recibido: {feedback_data}")
        return {
            "ok": True,
            "message": "feedback recibido"
        }
    except Exception as e:
        logger.exception("error al guardar el feedback")
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


if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8080"))
    import uvicorn  # type: ignore

    uvicorn.run("main:app", host=host, port=port, reload=False)
