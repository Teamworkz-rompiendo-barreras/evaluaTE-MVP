# backend/main.py
import json
import logging
import os
import base64
import uuid as uuid_lib
import datetime
from typing import Any, Dict, Optional
from sqlalchemy import create_engine, text
from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile, Depends

try:
    from backend.env_loader import load_backend_env
except ImportError:
    from env_loader import load_backend_env

load_backend_env()
from fastapi.middleware.cors import CORSMiddleware

try:
    from backend.auth import get_current_user, create_access_token
    from backend.pdf_service import router as pdf_router
    from backend.report_engine import run_employability_analysis
except ImportError:
    from auth import get_current_user, create_access_token
    from pdf_service import router as pdf_router
    from report_engine import run_employability_analysis

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

database_engine = None
_database_url = os.getenv("BACKEND_DATABASE_URL", "") or os.getenv("DATABASE_URL", "")
if _database_url:
    try:
        database_engine = create_engine(_database_url, pool_pre_ping=True, pool_recycle=300)
        logger.info("TiDB/MySQL inicializada en API Gateway.")
    except Exception as _e:
        logger.warning(f"Fallo de conexión TiDB en Gateway: {_e}")

app = FastAPI(title="EvaluaTE API Gateway", version="6.0.0 Serverless")

origins = [
    "http://localhost:3005",
    "http://127.0.0.1:3005",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://evaluate.teamworkz.co",
    "https://evalua-te-mvp.vercel.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex=r"https://evalua-te-mvp.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(pdf_router)


@app.post("/api/auth/guest-token")
async def generate_guest_session():
    guest_id = f"usr_{uuid_lib.uuid4().hex}"
    access_token = create_access_token(data={"sub": guest_id})
    return {"access_token": access_token, "token_type": "bearer", "user_id": guest_id}


@app.post("/api/informe-ia/feedback")
async def submit_feedback(request: Request, user_id: str = Depends(get_current_user)):
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="JSON inválido")

    record_id = str(uuid_lib.uuid4())
    rating = body.get("rating", "No especificado")
    comment = body.get("comment", "")
    timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()

    if not database_engine:
        raise HTTPException(status_code=503, detail="Base de datos de métricas inactiva")

    try:
        with database_engine.begin() as conn:
            conn.execute(
                text("INSERT INTO feedback_ia (id, user_id, rating, comment, timestamp) VALUES (:id, :user_id, :rating, :comment, :timestamp)"),
                {"id": record_id, "user_id": user_id, "rating": rating, "comment": comment, "timestamp": timestamp}
            )
    except Exception as _e:
        logger.error(f"Error al guardar feedback: {_e}")
        raise HTTPException(status_code=500, detail="Error de persistencia en métricas")

    return {"status": "registrado", "id": record_id}


@app.get("/api/report/latest")
async def get_latest_report(user_id: str = Depends(get_current_user)) -> Dict[str, Any]:
    if not database_engine:
        raise HTTPException(status_code=503, detail="Base de datos temporalmente desconectada.")

    try:
        with database_engine.connect() as conn:
            result = conn.execute(
                text("SELECT report_json FROM employability_reports WHERE user_id = :user_id ORDER BY created_at DESC LIMIT 1"),
                {"user_id": user_id}
            ).fetchone()

        if not result:
            raise HTTPException(status_code=404, detail="No se encontró ningún informe asociado a este perfil.")

        row = dict(result._mapping)
        raw_json = row.get("report_json")
        return json.loads(raw_json) if isinstance(raw_json, str) else (raw_json or {})
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error extrayendo reporte de BD: {e}")
        raise HTTPException(status_code=500, detail="Error interno de persistencia.")


@app.post("/api/analyze")
async def analyze_cv(
    request: Request,
    cv_file: Optional[UploadFile] = File(None),
    file: Optional[UploadFile] = File(None),
    game_results: str = Form("{}"),
    preferences: str = Form("{}"),
    user_id: str = Depends(get_current_user)
):
    try:
        games_data = json.loads(game_results)
        prefs_data = json.loads(preferences)
    except json.JSONDecodeError:
        games_data, prefs_data = {}, {}

    candidate_name = prefs_data.get("fullName", "Candidato")
    actual_file = cv_file or file
    pdf_bytes = None

    if actual_file:
        pdf_bytes = await actual_file.read()
    else:
        try:
            body = await request.json()
            b64_data = body.get("file_base64", "")
            if "," in b64_data: b64_data = b64_data.split(",")[1]
            if b64_data: pdf_bytes = base64.b64decode(b64_data)
        except Exception:
            pass

    if not pdf_bytes:
        raise HTTPException(status_code=400, detail="Documento PDF ausente o ilegible.")

    soft_skills_data = games_data.get("softSkills", [{"skill": "Toma de decisiones", "score": 80, "level": "Alto"}])
    avg_soft = 70
    try:
        avg_soft = int(sum(s.get("score", 0) for s in soft_skills_data) / max(1, len(soft_skills_data)))
    except Exception:
        pass

    employability_score = min(100, avg_soft + 10)
    level = "alto" if employability_score >= 80 else "medio"

    def _safe_score(skill_obj):
        try:
            return int(skill_obj.get("score", 100)) if isinstance(skill_obj, dict) else 100
        except (ValueError, TypeError):
            return 100

    sorted_skills = sorted(soft_skills_data, key=_safe_score)
    lowest_skills = [s.get("skill") for s in sorted_skills[:2] if isinstance(s, dict) and s.get("skill")]
    lowest_skills_str = ", ".join(lowest_skills) if lowest_skills else "No especificadas"

    result = await run_employability_analysis(
        pdf_bytes=pdf_bytes,
        user_id=user_id,
        games_data=games_data,
        prefs_data=prefs_data,
        employability_score=employability_score,
        level=level,
        lowest_skills_str=lowest_skills_str,
        candidate_name=candidate_name,
        database_engine=database_engine,
    )

    if result.get("status") == "error":
        raise HTTPException(status_code=502, detail=result.get("error", "Fallo en el análisis de IA."))

    return result


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=False)
