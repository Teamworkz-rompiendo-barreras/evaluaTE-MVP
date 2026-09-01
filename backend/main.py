# backend/main.py
import json
import logging
import os
import base64
import uuid as uuid_lib
import datetime
import asyncio
import sys  # FIX: Importación requerida para detectar el SO
from typing import Any, Dict, Optional
from sqlalchemy import create_engine, text
from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile, status, Depends

try:
    from backend.env_loader import load_backend_env
except ImportError:
    from env_loader import load_backend_env

load_backend_env()
from fastapi.middleware.cors import CORSMiddleware
from arq import create_pool
from arq.connections import RedisSettings
from arq.jobs import Job

# FIX ARQUITECTURA WINDOWS: Forzar el Event Loop correcto para soportar subprocesos (Playwright/Chromium)
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

try:
    from backend.cv_analyzer import extract_pdf_info
    from backend.auth import get_current_user, create_access_token
    from backend.storage import upload_pdf
    from backend.pdf_service import router as pdf_router
except ImportError:
    from cv_analyzer import extract_pdf_info
    from auth import get_current_user, create_access_token
    from storage import upload_pdf
    from pdf_service import router as pdf_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

database_engine = None
_database_url = os.getenv("BACKEND_DATABASE_URL", "")
if _database_url:
    try:
        database_engine = create_engine(_database_url, pool_pre_ping=True, pool_recycle=300)
        logger.info("TiDB/MySQL inicializada en API Gateway.")
    except Exception as _e:
        logger.warning(f"Fallo de conexión TiDB en Gateway: {_e}")

app = FastAPI(title="EvaluaTE API Gateway", version="5.8.4 Enterprise OS-Resilient")

origins = [
    "http://localhost:3005",
    "http://127.0.0.1:3005",
    "http://localhost:8080",
    "http://127.0.0.1:8080",
    "https://evaluate.teamworkz.co"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(pdf_router)

redis_pool = None

@app.on_event("startup")
async def startup_event():
    global redis_pool
    redis_url = os.getenv("REDIS_URL", "redis://127.0.0.1:6379")
    max_intentos = 5
    espera_segundos = 2

    for intento in range(1, max_intentos + 1):
        try:
            logger.info(f"Intentando conectar a Redis (Intento {intento}/{max_intentos})...")
            redis_pool = await create_pool(RedisSettings.from_dsn(redis_url))
            logger.info("Conexión con Redis Pool (ARQ) establecida exitosamente.")
            return
        except Exception as e:
            logger.warning(f"Fallo al conectar a Redis: {e}. Reintentando en {espera_segundos}s...")
            if intento == max_intentos:
                logger.critical("FATAL: No se pudo establecer conexión con Redis tras múltiples intentos.")
                redis_pool = None
            else:
                await asyncio.sleep(espera_segundos)


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


@app.post("/api/analyze", status_code=status.HTTP_202_ACCEPTED)
async def enqueue_analysis(
    request: Request,
    cv_file: Optional[UploadFile] = File(None),
    file: Optional[UploadFile] = File(None),
    game_results: str = Form("{}"),
    preferences: str = Form("{}"),
    user_id: str = Depends(get_current_user)
):
    if not redis_pool:
        raise HTTPException(status_code=503, detail="El sistema de colas no está disponible.")
    
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

    file_key = f"{user_id}_{uuid_lib.uuid4().hex}.pdf"
    try:
        upload_pdf(pdf_bytes, file_key)
    except Exception as e:
        logger.error(f"Error subiendo a MinIO: {e}")
        raise HTTPException(status_code=502, detail="Servicio de almacenamiento inalcanzable.")

    soft_skills_data = games_data.get("softSkills", [{"skill": "Toma de decisiones", "score": 80, "level": "Alto"}])
    avg_soft = 70
    try:
        avg_soft = int(sum(s.get("score", 0) for s in soft_skills_data) / max(1, len(soft_skills_data)))
    except Exception: pass
    
    employability_score = min(100, avg_soft + 10)
    level = "alto" if employability_score >= 80 else "medio"
    
    def _safe_score(skill_obj):
        try: return int(skill_obj.get("score", 100)) if isinstance(skill_obj, dict) else 100
        except (ValueError, TypeError): return 100
        
    sorted_skills = sorted(soft_skills_data, key=_safe_score)
    lowest_skills = [s.get("skill") for s in sorted_skills[:2] if isinstance(s, dict) and s.get("skill")]
    lowest_skills_str = ", ".join(lowest_skills) if lowest_skills else "No especificadas"

    try:
        job = await redis_pool.enqueue_job(
            "procesar_informe_ia", 
            user_id, file_key, games_data, prefs_data, employability_score, level, lowest_skills_str, candidate_name
        )
        return {
            "status": "encolado",
            "message": "Evaluación en clúster de IA.",
            "job_id": job.job_id
        }
    except Exception as e:
        logger.error(f"Fallo al encolar: {e}")
        raise HTTPException(status_code=500, detail="Error de infraestructura de colas.")


@app.get("/api/report/status/{job_id}")
async def check_job_status(job_id: str, user_id: str = Depends(get_current_user)):
    if not redis_pool:
        raise HTTPException(status_code=503, detail="Sistema de colas inactivo.")
    
    try:
        job = Job(job_id, redis_pool)
        status_job = await job.status()
        
        status_val = getattr(status_job, "value", str(status_job)).lower().replace('jobstatus.', '')
        
        if status_val == "not_found":
            return {"status": "error", "error": "ID de tarea no encontrado o expirado en Redis."}
            
        if status_val in ["queued", "in_progress", "deferred"]:
            return {"status": "procesando", "progress": "Evaluación cognitiva en curso..."}
            
        if status_val == "complete":
            try:
                result = await job.result()
                if isinstance(result, dict) and result.get("status") == "error":
                    return {"status": "error", "error": result.get("error", "Error crítico en procesamiento de IA.")}
                
                report_content = result.get("report", result) if isinstance(result, dict) else result
                return {"status": "completado", "report": report_content}
            except Exception as worker_err:
                logger.error(f"Fallo extrayendo resultado del Worker: {worker_err}", exc_info=True)
                return {"status": "error", "error": "Error interno al procesar el resultado de la IA."}
                
        if status_val in ["failed", "cancelled"]:
            return {"status": "error", "error": f"La tarea finalizó con estado: {status_val}"}
            
        return {"status": "procesando", "progress": f"Estado actual: {status_val}"}
        
    except Exception as e:
        logger.error(f"Error crítico en check_job_status: {e}", exc_info=True)
        return {"status": "error", "error": "Error de comunicación con el motor de colas."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=False)