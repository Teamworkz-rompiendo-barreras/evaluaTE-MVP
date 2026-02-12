import json
import logging
import os
import time
from typing import Any, Dict, List, Optional

try:
    import google.generativeai as genai
except ImportError:
    try:
        from backend import gemini_lite as genai
    except ImportError:
        import gemini_lite as genai
from fastapi import FastAPI, File, Form, HTTPException, Request, Response, UploadFile
from fastapi.middleware.cors import CORSMiddleware

# Importaciones locales
try:
    from backend.cv_analyzer import extract_pdf_info
    from backend.prompt_config import PromptConfig
    from backend.new_report_schema import NewReportSchema
except ImportError:
    # Fallback para ejecución directa
    from cv_analyzer import extract_pdf_info
    from prompt_config import PromptConfig
    from new_report_schema import NewReportSchema

# pdf_service is optional (requires reportlab which is not in serverless)
create_employability_pdf = None
try:
    from backend.pdf_service import create_employability_pdf
except ImportError:
    try:
        from pdf_service import create_employability_pdf
    except ImportError:
        pass  # create_employability_pdf stays None

# Configurar logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configurar Gemini
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
if not GOOGLE_API_KEY:
    logger.warning("GOOGLE_API_KEY no está configurada. La IA no funcionará correctamente.")
else:
    genai.configure(api_key=GOOGLE_API_KEY)

APP_TITLE = os.getenv("APP_TITLE", "EvaluaTE Backend")
APP_VERSION = "2.0.0 - Gemini Integration"

app = FastAPI(title=APP_TITLE, version=APP_VERSION)

# Configuración CORS
allowed_origins_env = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:3000,http://localhost:5173,https://evalua-te-mvp.vercel.app"
)
ALLOWED_ORIGINS = [o.strip() for o in allowed_origins_env.split(",") if o.strip()]

# En producción, asegurarse de que los orígenes permitidos incluyan la URL de Vercel
if os.getenv("PRODUCTION", "false").lower() == "true":
    default_domains = [
        "https://evalua-te-mvp.vercel.app",
    ]
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


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "evaluate-backend", "version": APP_VERSION}

# Configurar Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase_client = None

if SUPABASE_URL and SUPABASE_KEY:
    try:
        from supabase import create_client, Client
        supabase_client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        logger.info("Supabase client initialized")
    except ImportError:
        logger.warning("Supabase library not found. Install it with `pip install supabase`")
    except Exception as e:
        logger.error(f"Failed to initialize Supabase client: {e}")

@app.post("/api/analyze")
async def analyze_computational_profile(
    request: Request,
    cv_file: Optional[UploadFile] = File(None),
    game_results: str = Form(...),
    preferences: str = Form(...)
):
    """
    Endpoint principal para generar el informe de empleabilidad.
    Recibe:
    - cv_file: Archivo PDF o imagen del CV (Opcional).
    - game_results: JSON string con los resultados de los juegos.
    - preferences: JSON string con las preferencias del candidato.
    """
    try:
        # Get user_id from header if authenticated (set by frontend/gateway)
        # For MVP without full backend auth middleware, we might accept it from a header or form
        # Warning: In production, validate this via a proper JWT token
        user_id = request.headers.get("X-User-Id")
        
        # 1. Parsear datos del formulario
        try:
            games_data = json.loads(game_results)
            prefs_data = json.loads(preferences)
        except json.JSONDecodeError as e:
            raise HTTPException(status_code=400, detail=f"Error al decodificar JSON: {e}")

        # 2. Leer y extraer texto del CV (si existe)
        cv_data = {}
        full_text = ""
        
        if cv_file:
            pdf_bytes = await cv_file.read()
            if pdf_bytes:
                cv_extraction = await extract_pdf_info(pdf_bytes)
                if cv_extraction:
                    cv_data = cv_extraction.get("cv_info", {})
                    full_text = cv_extraction.get("raw_text", "")
        
        # Si no hay CV, cv_data y full_text quedan vacíos, el prompt debe manejarlo.
        
        # 3. Preparar datos para el prompt
        candidate_name = cv_data.get("contact", {}).get("name") or "Candidato"
        
        # Calcular/Extraer score de empleabilidad (mock o calculado)
        employability_score = 75 # Placeholder
        level = "medio" # Placeholder

        if isinstance(games_data, list):
             # Legacy/Simpler format where games_data is just a list of games
             completed_games_list = [g.get("name", "Juego desconocido") for g in games_data]
             soft_skills_data = [] # Fallback
        elif isinstance(games_data, dict):
             # Rich format from frontend
             completed_games_list = games_data.get("completedGames", [])
             # Extract explicit skill objects
             soft_skills_data = games_data.get("softSkills", [])
        else:
             completed_games_list = []
             soft_skills_data = []

        # Fallback if no soft skills provided
        if not soft_skills_data:
             soft_skills_data = [
                {"skill": "Resolución de problemas", "score": 80, "level": "alto"},
                {"skill": "Adaptabilidad", "score": 75, "level": "medio"},
                {"skill": "Atención al detalle", "score": 85, "level": "alto"}
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
            languages_data=cv_data.get("languages", []),
            full_raw_text=full_text
        )

        # 5. Llamar a Gemini
        if not GOOGLE_API_KEY:
             logger.warning("API Key no configurada, retornando mock data")
             # Retornar JSON Mock seguro
             return {
                 "summary": "Informe MOCK generado porque no hay API Key.",
                 "personal_data": {"name": candidate_name, "location": "Madrid", "email": "mock@email.com", "phone": "600000000", "disability_certificate": "No consta"},
                 "profile_summary": "Este es un resumen simulado.",
                 "cv_summary": "Resumen del CV simulado.",
                 "strengths": ["Simulación", "Test"],
                 "improvement_areas": [{"area": "Mock", "reason": "No API", "suggested_action": "Configurar API Key"}],
                 "cv_analysis": {
                     "structure_score": 3, "coherence_score": 3, "key_info_score": 3, "clarity_score": 3, "style_score": 3,
                     "evidence": {"structure": "ok", "coherence": "ok", "key_info": "ok", "clarity": "ok", "style": "ok"},
                     "corrections": [], "reordering_suggestions": []
                 },
                 "ideal_work_environment": "Remoto",
                 "suggested_roles": [{"role": "Desarrollador Mock", "reason": "Test", "seniority": "Junior", "remote_viable": True}],
                 "action_plan": {"short_term": ["Test"], "medium_term": ["Test"], "long_term": ["Test"]},
                 "job_search_advice": {"cv_optimization": [], "letters_portfolio": "", "recommended_platforms": [], "networking": "", "interview_tips": ""},
                 "useful_tools": {"productivity": [], "job_search": [], "learning": [], "accessibility": []},
                 "completed_games": completed_games_list,
                 "ready_phrases": {"headline": "Mock", "about_me": "Mock", "short_message": "Mock"},
                 "final_message": "Mock message"
             }

        model = genai.GenerativeModel('gemini-1.5-flash')
        generation_config = genai.types.GenerationConfig(
            response_mime_type="application/json"
        )
        
        response = await model.generate_content_async(
            prompt,
            generation_config=generation_config
        )
        
        response_text = response.text
        
        # 6. Parsear y validar JSON de respuesta
        try:
            analysis_result = json.loads(response_text)
        except json.JSONDecodeError:
            start = response_text.find('{')
            end = response_text.rfind('}') + 1
            if start != -1 and end != -1:
                analysis_result = json.loads(response_text[start:end])
            else:
                raise HTTPException(status_code=500, detail="La IA no generó un JSON válido")

        # 7. Persistir en Supabase (si está configurado y tenemos user_id)
        if supabase_client and user_id:
            try:
                # Prepare data for employability_reports
                # Note: employability_score and level might be recalculated or taken from AI result
                # For now, we use the placeholder or parsed values
                
                # Try to extract score/level from analysis_result if present, else fallback
                final_score = analysis_result.get("employability_score", employability_score)
                final_level = analysis_result.get("level", level) # AI doesn't explicitly return level in root usually

                report_payload = {
                    "user_id": user_id,
                    "employability_score": final_score,
                    "level": str(final_level),
                    "report_json": analysis_result,
                    "created_at": "now()"
                }
                
                data, count = supabase_client.table("employability_reports").insert(report_payload).execute()
                logger.info(f"Report saved to Supabase for user {user_id}")
                
            except Exception as db_err:
                logger.error(f"Error saving to Supabase: {db_err}")
                # Don't fail the request if DB save fails, just log it
                pass

        return analysis_result

    except Exception as e:
        logger.exception("Error en /api/analyze")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/report/generate")
async def generate_pdf_report(report_data: dict, filename: Optional[str] = "reporte_empleabilidad.pdf"):
    """
    Genera el PDF a partir del JSON del informe.
    """
    try:
        pdf_bytes = create_employability_pdf(report_data)
        
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        logger.exception("Error generando PDF")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/debug/cv_data")
async def api_debug_cv_data(file: UploadFile = File(...)) -> Dict[str, Any]:
    """Return the raw CV extraction JSON for debugging purposes."""
    try:
        pdf_bytes = await file.read()
        if not pdf_bytes:
            raise HTTPException(status_code=400, detail="Archivo vacío")
        result = await extract_pdf_info(pdf_bytes)
        logger.info("debug endpoint returned CV data")
        return result
    except Exception as e:
        logger.exception("Error in debug endpoint")
        raise HTTPException(status_code=500, detail=f"Error debug CV: {e}")

if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8080"))
    import uvicorn
    uvicorn.run("main:app", host=host, port=port, reload=False)
