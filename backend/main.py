import json
import logging
import os
import time
from typing import Any, Dict, List, Optional

from sqlalchemy import create_engine, text

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
    from backend.cv_structure_analyzer import (  # type: ignore
        analyze_cv_structure_from_bytes,
        extract_contact_info,
        review_to_ui_diagnostico,
    )
except ImportError:
    from cv_analyzer import extract_pdf_info, analyze_multimodal_report  # type: ignore
    from prompt_config import PromptConfig  # type: ignore
    from new_report_schema import NewReportSchema, convert_old_format_to_new  # type: ignore
    from cv_structure_analyzer import (  # type: ignore
        analyze_cv_structure_from_bytes,
        extract_contact_info,
        review_to_ui_diagnostico,
    )

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
APP_VERSION = "2.2.0 - New Report Format"


def _map_gemini_to_new_format(raw: dict, soft_skills: list, completed_games: list) -> dict:
    """Convierte el JSON en español que devuelve Gemini al formato NewReportSchema que espera el frontend."""
    dp = raw.get("datos_personales") or {}
    foda = raw.get("analisis_foda") or {}
    plan = raw.get("plan_accion") or {}
    kit = raw.get("kit_busqueda") or {}
    roles = raw.get("roles_sugeridos") or []
    frases = kit.get("frases_linkedin") or {}
    pasos = plan.get("pasos") or []
    optimizacion_cv = list(raw.get("optimizacion_cv") or [])

    def _split_pasos(items: list) -> dict:
        """Agrupa los pasos del plan de acción por horizonte temporal.

        Gemini suele etiquetar cada paso con un prefijo ("Corto plazo:",
        "Medio plazo:", "Largo plazo:"). Si los prefijos no están presentes
        (o solo se devuelven 2-4 pasos), se reparte la lista en tres bloques
        para que "Largo plazo" no quede vacío.
        """
        short, medium, long_ = [], [], []
        untagged = []
        for p in items:
            text = str(p).strip()
            low = text.lower()
            if low.startswith("corto plazo"):
                short.append(text)
            elif low.startswith(("medio plazo", "mediano plazo")):
                medium.append(text)
            elif low.startswith("largo plazo"):
                long_.append(text)
            else:
                untagged.append(text)

        if untagged:
            n = len(untagged)
            third = max(1, -(-n // 3))  # ceil(n/3)
            if not short:
                short = untagged[:third]
                untagged = untagged[third:]
            if not medium:
                medium = untagged[:third]
                untagged = untagged[third:]
            if not long_:
                long_ = untagged

        return {"short_term": short, "medium_term": medium, "long_term": long_}

    # Fallback: si Gemini no rellena "optimizacion_cv" (campo nuevo, a veces
    # omitido), reutilizamos las áreas de mejora del FODA como sugerencias.
    if not optimizacion_cv:
        optimizacion_cv = [str(a) for a in (foda.get("areas_mejora") or []) if a][:3]

    # Fallback genérico si Gemini no devuelve "pasos" en absoluto
    if not pasos:
        pasos = [
            "Corto plazo: Actualiza tu CV y perfil de LinkedIn con tus logros más recientes.",
            "Corto plazo: Prepara una lista de empresas objetivo y empieza a enviar candidaturas.",
            "Medio plazo: Refuerza tus habilidades técnicas o blandas con un curso corto.",
            "Medio plazo: Amplía tu red de contactos profesionales (networking).",
            "Largo plazo: Define un plan de desarrollo profesional a 6-12 meses.",
            "Largo plazo: Evalúa periódicamente tus avances y ajusta tus objetivos.",
        ]

    herramientas = list(plan.get("herramientas") or [])
    lecturas = list(plan.get("lecturas") or [])
    if not herramientas:
        herramientas = ["LinkedIn", "Trello", "Canva"]
    if not lecturas:
        lecturas = ["Blog de orientación laboral InfoJobs", "Podcast 'Aprendiendo de los mejores'"]

    name = str(dp.get("nombre") or "")
    if not name or name in ("Candidato", "Usuario", "<NOMBRE>"):
        name = "Usuario"

    def _exp_item(e: dict) -> dict:
        return {
            "title": str(e.get("rol") or e.get("title") or ""),
            "subtitle": str(e.get("empresa") or e.get("company") or ""),
            "period": str(e.get("periodo") or e.get("period") or ""),
            "detail": str(e.get("descripcion") or e.get("description") or ""),
        }

    def _edu_item(e: dict) -> dict:
        return {
            "title": str(e.get("titulo") or e.get("title") or e.get("degree") or ""),
            "subtitle": str(e.get("institucion") or e.get("institution") or ""),
            "period": str(e.get("periodo") or e.get("period") or ""),
        }

    def _lang_item(e: dict) -> dict:
        return {
            "title": str(e.get("idioma") or e.get("language") or e.get("name") or ""),
            "level": str(e.get("nivel") or e.get("level") or ""),
        }

    def _tool_item(h) -> dict:
        if isinstance(h, str):
            return {"title": h}
        if isinstance(h, dict):
            return {"title": str(h.get("herramienta") or h.get("skill") or h.get("name") or "")}
        return {"title": str(h)}

    cv_details = {
        "experience": [_exp_item(e) for e in (raw.get("experiencia") or []) if isinstance(e, dict) and (e.get("rol") or e.get("empresa"))],
        "education": [_edu_item(e) for e in (raw.get("educacion") or []) if isinstance(e, dict) and (e.get("titulo") or e.get("institucion"))],
        "languages": [_lang_item(e) for e in (raw.get("idiomas") or []) if isinstance(e, dict) and (e.get("idioma") or e.get("language"))],
        "tools": [_tool_item(h) for h in (raw.get("habilidades") or []) if h],
    }

    return {
        "personal_data": {
            "name": name,
            "location": str(dp.get("ubicacion") or "No consta"),
            "email": str(dp.get("email") or dp.get("contacto") or "No consta"),
            "phone": str(dp.get("telefono") or "No especificado"),
            "disability_certificate": str(dp.get("discapacidad") or ""),
        },
        "profile_summary": str(raw.get("resumen_ejecutivo") or ""),
        "summary": str(raw.get("resumen_ejecutivo") or ""),
        "cv_analysis_summary": str(raw.get("analisis_detallado_cv") or raw.get("resumen_cv") or ""),
        "cv_details": cv_details,
        "strengths": list(foda.get("fortalezas_clave") or []),
        "soft_skills": soft_skills,
        "improvement_areas": [
            {"area": str(a), "reason": "", "suggested_action": ""}
            for a in (foda.get("areas_mejora") or [])
            if a
        ],
        "cv_analysis": {
            "structure_score": 0, "coherence_score": 0, "key_info_score": 0,
            "clarity_score": 0, "style_score": 0,
            "evidence": {"structure": "", "coherence": "", "key_info": "", "clarity": "", "style": ""},
            "corrections": [], "reordering_suggestions": [],
        },
        "ideal_work_environment": ", ".join(str(e) for e in (raw.get("entornos_ideales") or [])),
        "suggested_roles": [
            {
                "role": str(r.get("rol") or ""),
                "reason": str(r.get("justificacion") or r.get("ajuste") or ""),
                "seniority": "",
                "remote_viable": False,
            }
            for r in roles if isinstance(r, dict)
        ],
        "action_plan": _split_pasos(pasos),
        "job_search_advice": {
            "cv_optimization": optimizacion_cv,
            "letters_portfolio": [],
            "recommended_platforms": herramientas,
            "networking": [],
            "interview_tips": [],
        },
        "useful_tools": {
            "productivity": herramientas,
            "job_search": [],
            "learning": lecturas,
            "accessibility": [],
        },
        "ready_phrases": {
            "headline": str(frases.get("titular") or ""),
            "about_me": str(frases.get("acerca_de") or ""),
            "short_message": str(kit.get("mensaje_reclutador") or ""),
        },
        "employability_score": 0,
        "completed_games": [str(g) for g in completed_games],
        "final_message": str(raw.get("mensaje_final_azul") or raw.get("capitalizar_fortalezas") or ""),
        "job_preferences": {},
    }

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
# GET /api/report/latest — Carga el último informe generado para el usuario
# ──────────────────────────────────────────────────────────────────────
@app.get("/api/report/latest")
async def get_latest_report(request: Request) -> Dict[str, Any]:
    """
    Devuelve el informe más reciente del usuario desde Supabase (sin regenerar).
    Requiere cabecera X-User-Id.
    """
    user_id = request.headers.get("X-User-Id")
    if not user_id:
        raise HTTPException(status_code=400, detail="X-User-Id header required")
    if not supabase_client:
        raise HTTPException(status_code=503, detail="Database not available")
    try:
        res = (
            supabase_client.table("employability_reports")
            .select("report_json, employability_score, created_at")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .limit(1)
            .execute()
        )
        rows = res.data or []
        if not rows:
            raise HTTPException(status_code=404, detail="No report found")

        row = rows[0]
        analysis_result = row.get("report_json") or {}
        employability_score = row.get("employability_score") or 0

        soft_skills_raw = analysis_result.get("soft_skills") or []
        completed_games = analysis_result.get("completed_games") or []
        new_format = _map_gemini_to_new_format(analysis_result, soft_skills_raw, completed_games)
        new_format["employability_score"] = employability_score

        # Re-compute CV scores (same logic as /api/analyze)
        try:
            try:
                from backend.cv_structure_analyzer import compute_review_from_text_sections, review_to_ui_diagnostico  # type: ignore
            except ImportError:
                from cv_structure_analyzer import compute_review_from_text_sections, review_to_ui_diagnostico  # type: ignore
            raw_ai = analysis_result or {}
            dp = raw_ai.get("datos_personales") or {}
            text_parts = [
                str(raw_ai.get("resumen_ejecutivo") or ""),
                str(dp.get("email") or ""), str(dp.get("telefono") or ""), str(dp.get("ubicacion") or ""),
            ]
            for exp in (raw_ai.get("experiencia") or []):
                if isinstance(exp, dict):
                    text_parts.extend(str(v) for v in exp.values() if v)
            for edu in (raw_ai.get("educacion") or []):
                if isinstance(edu, dict):
                    text_parts.extend(str(v) for v in edu.values() if v)
            for skill in (raw_ai.get("habilidades") or raw_ai.get("habilidades_detectadas") or []):
                text_parts.append(str(skill.get("herramienta") or skill) if isinstance(skill, dict) else str(skill))
            cv_text = " ".join(filter(None, text_parts))
            exp_items = raw_ai.get("experiencia") or []
            cv_sections = {k: v for k, v in {
                "experience": [" ".join(str(v) for v in e.values() if v) if isinstance(e, dict) else str(e) for e in exp_items],
                "education": raw_ai.get("educacion"),
                "languages": raw_ai.get("idiomas"),
                "contact": dp if any(dp.get(k) for k in ("email", "telefono", "nombre")) else None,
                "profile": raw_ai.get("resumen_ejecutivo"),
                "skills": raw_ai.get("habilidades") or raw_ai.get("habilidades_detectadas"),
            }.items() if v}
            review = compute_review_from_text_sections(cv_text, cv_sections)
            cv_scores = review_to_ui_diagnostico(review)
            if "spelling_style_score" in cv_scores and "style_score" not in cv_scores:
                cv_scores["style_score"] = cv_scores.pop("spelling_style_score")
            if isinstance(new_format.get("cv_analysis"), dict):
                keep = ("structure_score", "coherence_score", "key_info_score", "clarity_score",
                        "style_score", "evidence", "corrections", "reordering_suggestions")
                new_format["cv_analysis"].update({k: cv_scores[k] for k in keep if k in cv_scores})
        except Exception as cv_err:
            logger.warning(f"CV scoring skipped in GET /api/report/latest: {cv_err}")

        return new_format

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error in GET /api/report/latest")
        raise HTTPException(status_code=500, detail=str(e))


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
                full_raw_text="",
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
            
            model = genai.GenerativeModel("gemini-flash-latest")
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

        new_format = _map_gemini_to_new_format(analysis_result, soft_skills_data, completed_games_list)

        # Compute real CV structure scores (1-5 stars) from AI analysis result
        try:
            try:
                from backend.cv_structure_analyzer import compute_review_from_text_sections, review_to_ui_diagnostico  # type: ignore
            except ImportError:
                from cv_structure_analyzer import compute_review_from_text_sections, review_to_ui_diagnostico  # type: ignore
            raw_ai = analysis_result or {}
            dp = raw_ai.get("datos_personales") or {}

            # Build a text proxy for heuristic scoring
            # Keys come from the AI prompt schema (Spanish): resumen_ejecutivo, habilidades (str list)
            text_parts = [
                str(raw_ai.get("resumen_ejecutivo") or ""),
                str(dp.get("email") or ""),
                str(dp.get("telefono") or ""),
                str(dp.get("ubicacion") or ""),
            ]
            for exp in (raw_ai.get("experiencia") or []):
                if isinstance(exp, dict):
                    text_parts.extend(str(v) for v in exp.values() if v)
            for edu in (raw_ai.get("educacion") or []):
                if isinstance(edu, dict):
                    text_parts.extend(str(v) for v in edu.values() if v)
            # habilidades is a plain string list in the AI output
            for skill in (raw_ai.get("habilidades") or raw_ai.get("habilidades_detectadas") or []):
                text_parts.append(str(skill.get("herramienta") or skill) if isinstance(skill, dict) else str(skill))

            cv_text = " ".join(filter(None, text_parts))

            # Build sections dict using keys expected by compute_review_from_text_sections
            exp_items = raw_ai.get("experiencia") or []
            cv_sections = {k: v for k, v in {
                "experience": [" ".join(str(v) for v in e.values() if v) if isinstance(e, dict) else str(e) for e in exp_items],
                "education": raw_ai.get("educacion"),
                "languages": raw_ai.get("idiomas"),
                "contact": dp if any(dp.get(k) for k in ("email", "telefono", "nombre")) else None,
                "profile": raw_ai.get("resumen_ejecutivo"),
                "skills": raw_ai.get("habilidades") or raw_ai.get("habilidades_detectadas"),
            }.items() if v}

            review = compute_review_from_text_sections(cv_text, cv_sections)
            cv_scores = review_to_ui_diagnostico(review)

            # Normalise key name: spelling_style_score → style_score
            if "spelling_style_score" in cv_scores and "style_score" not in cv_scores:
                cv_scores["style_score"] = cv_scores.pop("spelling_style_score")

            if isinstance(new_format.get("cv_analysis"), dict):
                keep = ("structure_score", "coherence_score", "key_info_score", "clarity_score",
                        "style_score", "evidence", "corrections", "reordering_suggestions")
                new_format["cv_analysis"].update({k: cv_scores[k] for k in keep if k in cv_scores})
        except Exception as cv_err:
            logger.warning(f"CV structure scoring skipped: {cv_err}")

        return new_format

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
    Análisis estructural local (PyMuPDF + heurísticas), SIN llamar a Gemini,
    para no consumir la cuota de IA en la vista previa de subida del CV.
    El informe final (/api/analyze) sí usa IA para extraer experiencia,
    educación, etc. en detalle.
    """
    try:
        pdf_bytes = await cv_file.read()
        if not pdf_bytes:
            raise HTTPException(status_code=400, detail="Empty file")

        result = await _asyncio.to_thread(analyze_cv_structure_from_bytes, pdf_bytes)
        review = result["review"]
        text = result["text"]
        sections = result["sections"]

        diagnostico = review_to_ui_diagnostico(review)
        contact_info = extract_contact_info(text)

        contact = {
            "name": contact_info.get("nombre", ""),
            "emails": [contact_info["email"]] if contact_info.get("email") else [],
            "phones": [contact_info["telefono"]] if contact_info.get("telefono") else [],
            "location": "",
            "linkedin": contact_info.get("linkedin", ""),
        }

        corrections = list(diagnostico.get("corrections") or [])
        if not contact["emails"]:
            corrections.append("Añade un email de contacto")
        if not contact["phones"]:
            corrections.append("Añade un teléfono de contacto")
        if not sections.get("profile"):
            corrections.append("Añade un resumen/perfil profesional")
        if not sections.get("education"):
            corrections.append("Añade tu formación académica")

        return {
            "structure_score": diagnostico["structure_score"],
            "coherence_score": diagnostico["coherence_score"],
            "key_info_score": diagnostico["key_info_score"],
            "clarity_score": diagnostico["clarity_score"],
            "style_score": diagnostico["spelling_style_score"],
            "evidence": diagnostico["evidence"],
            "corrections": corrections,
            "reordering_suggestions": [],
            "experience_detailed": [],
            "education_detailed": [],
            "languages": [],
            "software": [],
            "contact": contact,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error en /api/pdf/analyze-cv")
        raise HTTPException(status_code=500, detail=str(e))

# --- TiDB / MySQL config ---
database_engine = None
_database_url = os.getenv("DATABASE_URL", "")

if _database_url:
    try:
        database_engine = create_engine(
            _database_url,
            pool_pre_ping=True,
            pool_recycle=300
        )
        logger.info("TiDB/MySQL connection initialized")
    except Exception as _e:
        logger.warning(f"TiDB/MySQL init failed: {_e}")


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

    # Guardar en TiDB/MySQL
    if not database_engine:
        logger.error("DATABASE_URL no está configurada o database_engine es None")
        raise HTTPException(
            status_code=500,
            detail="DATABASE_URL no está configurada o database_engine es None"
        )
    try:
        with database_engine.begin() as conn:
            conn.execute(
                text("""
                    INSERT INTO feedback_ia (id, rating, comment, timestamp, user_data)
                    VALUES (:id, :rating, :comment, :timestamp, :user_data)
                """),
                {
                    "id": record["id"],
                    "rating": record["rating"],
                    "comment": record["comment"],
                    "timestamp": record["timestamp"],
                    "user_data": json.dumps(record["user_data"], ensure_ascii=False),
                }
            )

        logger.info(f"Feedback saved to TiDB/MySQL: {record['id']}")

    except Exception as e:
        logger.error(f"TiDB/MySQL insert failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"TiDB/MySQL insert failed: {e}"
        )

    # Notificar por email sin romper el endpoint
    try:
        _send_feedback_email(record)
    except Exception as e:
        logger.error(f"Feedback email failed: {e}")

    logger.info(f"Feedback received: rating={record['rating']}")
    return {"ok": True, "id": record["id"]}

@app.get("/api/informe-ia/feedback/stats")
async def feedback_stats():
    """Devuelve estadísticas de feedback para el dashboard."""
    if not database_engine:
        return {
            "total_feedback": 0,
            "useful_feedback": 0,
            "not_useful_feedback": 0,
            "satisfaction_rate": 0,
            "recent_feedback": [],
        }
    try:
        with database_engine.connect() as conn:
            result = conn.execute(
                text("""
                    SELECT id, rating, comment, timestamp, user_data, created_at
                    FROM feedback_ia
                    ORDER BY timestamp DESC
                    LIMIT 100
                """)
            )

            rows = []
            for row in result:
                item = dict(row._mapping)

                if item.get("timestamp"):
                    item["timestamp"] = item["timestamp"].isoformat()

                if item.get("created_at"):
                    item["created_at"] = item["created_at"].isoformat()

                rows.append(item)

        useful = [r for r in rows if r.get("rating") == "Útil"]
        not_useful = [r for r in rows if r.get("rating") != "Útil"]
        total = len(rows)

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
