# -*- coding: utf-8 -*-
import os
import sys
import smtplib
import datetime
import uuid as uuid_lib
import logging
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, text

logger = logging.getLogger(__name__)

# ==========================================
# CONFIGURACIÓN DE ENTORNO Y BASES DE DATOS
# ==========================================
SMTP_HOST  = os.getenv("SMTP_HOST", "")
SMTP_PORT  = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER  = os.getenv("SMTP_USER", "")
SMTP_PASS  = os.getenv("SMTP_PASSWORD", "")
FROM_EMAIL = os.getenv("FROM_EMAIL", SMTP_USER)
FEEDBACK_TO = os.getenv("FEEDBACK_EMAIL", "hola@teamwork.co")

supabase_client = None
_supabase_url = os.getenv("SUPABASE_URL", "")
_supabase_key = os.getenv("SUPABASE_KEY", "")
if _supabase_url and _supabase_key:
    try:
        from supabase import create_client
        supabase_client = create_client(_supabase_url, _supabase_key)
    except Exception as _e:
        logger.warning(f"Supabase init failed: {_e}")

database_engine = None
_database_url = os.getenv("DATABASE_URL", "")
if _database_url:
    try:
        database_engine = create_engine(_database_url, pool_pre_ping=True, pool_recycle=300)
        logger.info("TiDB/MySQL connection initialized")
    except Exception as _e:
        logger.warning(f"TiDB/MySQL init failed: {_e}")

# ==========================================
# INICIALIZACIÓN DE FASTAPI
# ==========================================
app = FastAPI(title="evaluaTE API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================
# RESOLUCIÓN DE RUTAS DEL BACKEND PRINCIPAL
# ==========================================
_using_backend = False
_backend_error = None
_file_dir = os.path.dirname(os.path.abspath(__file__))
_backend_search = [_file_dir, os.path.dirname(_file_dir)]

for _candidate_root in _backend_search:
    if os.path.isdir(os.path.join(_candidate_root, "backend")):
        if _candidate_root not in sys.path:
            sys.path.insert(0, _candidate_root)
        try:
            from backend.main import app as _backend_app  # type: ignore
            app = _backend_app
            _using_backend = True
        except Exception as _be:
            import traceback as _tb
            _backend_error = f"{type(_be).__name__}: {_be}\n{_tb.format_exc()}"
            logger.warning(f"Backend import failed: {_be}")
        break

# ==========================================
# RUTAS DE FALLBACK (MODO STANDALONE)
# Se ejecutan en Vercel si el backend principal falla o no se importa
# ==========================================
if not _using_backend:

    def _send_feedback_email(data: dict) -> None:
        if not (SMTP_HOST and SMTP_USER and SMTP_PASS):
            return
        try:
            icon = "👍" if data.get("rating") == "Útil" else "👎"
            msg = MIMEMultipart()
            msg["From"] = FROM_EMAIL
            msg["To"] = FEEDBACK_TO
            msg["Subject"] = f"[evaluaTE] Nuevo feedback: {data.get('rating', '?')}"
            body = (
                f"<html><body style='font-family:Arial,sans-serif;max-width:600px;margin:0 auto'>"
                f"<h2>{icon} Nuevo feedback en evaluaTE</h2>"
                f"<p><strong>Valoración:</strong> {data.get('rating', '?')}</p>"
                f"<p><strong>Comentario:</strong> {data.get('comment') or '(sin comentario)'}</p>"
                f"<p><strong>Fecha:</strong> {data.get('timestamp', '')}</p>"
                f"</body></html>"
            )
            msg.attach(MIMEText(body, "html"))
            with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as s:
                s.ehlo(); s.starttls(); s.ehlo()
                s.login(SMTP_USER, SMTP_PASS)
                s.sendmail(FROM_EMAIL, [FEEDBACK_TO], msg.as_string())
            logger.info(f"Feedback email sent to {FEEDBACK_TO}")
        except Exception as _e:
            logger.error(f"Error sending feedback email: {_e}")

    @app.get("/api/health")
    async def health():
        return {"status": "ok", "mode": "standalone"}

    @app.get("/api/auth/me")
    async def mock_auth():
        # Endpoint restaurado para desbloquear la UI (AuthContext) en modo standalone
        return {"user": None}

    @app.get("/api/debug/backend-error")
    async def debug_backend_error():
        # ⚠️ ADVERTENCIA: En un entorno de producción estricto, este endpoint debería estar protegido por un token.
        return {
            "backend_error": _backend_error,
            "file": __file__,
            "searched": _backend_search,
            "sys_path": sys.path[:5],
        }

    @app.post("/api/informe-ia/feedback")
    async def submit_feedback(request: Request):
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

        if not database_engine:
            logger.error("DATABASE_URL no está configurada o database_engine es None")
            raise HTTPException(status_code=500, detail="Base de datos no configurada")

        try:
            with database_engine.begin() as conn:
                conn.execute(
                    text("""
                        INSERT INTO feedback_ia (id, rating, comment, user_data)
                        VALUES (:id, :rating, :comment, :user_data)
                    """),
                    {
                        "id": record.get("id"),
                        "rating": record.get("rating"),
                        "comment": record.get("comment"),
                        "user_data": json.dumps(record.get("user_data", {}), ensure_ascii=False),
                    }
                )
        except Exception as _e:
            logger.error(f"TiDB/MySQL insert failed: {_e}")
            raise HTTPException(status_code=500, detail=f"Error en base de datos.")

        try:
            _send_feedback_email(record)
        except Exception as _e:
            logger.error(f"TiDB/MySQL message failed: {_e}")
            
        return {"ok": True, "id": record["id"]}

    @app.get("/api/informe-ia/feedback/stats")
    async def feedback_stats():
        if not database_engine:
            return {
                "total_feedback": 0,
                "useful_feedback": 0,
                "not_useful_feedback": 0,
                "satisfaction_rate": 0,
                "recent_feedback": []
            }

        try:
            with database_engine.connect() as conn:
                result = conn.execute(
                    text("""
                        SELECT id, rating, comment, user_data, `timestamp`, created_at
                        FROM feedback_ia
                        ORDER BY `timestamp` DESC
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
            total = len(rows)

            return {
                "total_feedback": total,
                "useful_feedback": len(useful),
                "not_useful_feedback": total - len(useful),
                "satisfaction_rate": round(len(useful) / total * 100, 1) if total else 0,
                "recent_feedback": rows[:20],
            }

        except Exception as _e:
            logger.error(f"Error fetching feedback stats from TiDB/MySQL: {_e}")
            return {
                "total_feedback": 0,
                "useful_feedback": 0,
                "not_useful_feedback": 0,
                "satisfaction_rate": 0,
                "recent_feedback": []
            }