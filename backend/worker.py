# backend/worker.py
import json
import logging
import uuid as uuid_lib
import os

try:
    from backend.env_loader import load_backend_env
except ImportError:
    from env_loader import load_backend_env

# CARGA OBLIGATORIA DE ENTORNO ANTES DE CUALQUIER IMPORTACIÓN DE NEGOCIO
load_backend_env()

# Puente de compatibilidad para el SDK de Google GenAI
raw_api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY") or os.getenv("GEMINI_KEY_1")
if raw_api_key:
    os.environ["GEMINI_API_KEY"] = raw_api_key.strip()
    os.environ["GOOGLE_API_KEY"] = raw_api_key.strip()

from typing import Dict, Any
from arq.connections import RedisSettings
from sqlalchemy import create_engine, text

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("worker")

db_url = os.getenv("BACKEND_DATABASE_URL")
if not db_url:
    logger.critical("FATAL: BACKEND_DATABASE_URL no está definida en el entorno.")
    database_engine = None
else:
    database_engine = create_engine(db_url, pool_pre_ping=True, pool_recycle=300)

try:
    from backend.cv_analyzer import extract_pdf_info, analyze_multimodal_report
    from backend.prompt_config import PromptConfig
    from backend.pii_masking import mask_pii_data
    from backend.storage import download_pdf, delete_pdf
except ImportError:
    from cv_analyzer import extract_pdf_info, analyze_multimodal_report
    from prompt_config import PromptConfig
    from pii_masking import mask_pii_data
    from storage import download_pdf, delete_pdf

async def procesar_informe_ia(
    ctx, user_id: str, file_key: str, games_data: dict, prefs_data: dict,
    employability_score: int, level: str, lowest_skills_str: str, candidate_name: str
) -> Dict[str, Any]:
    
    logger.info(f"Worker iniciando análisis para usuario: {user_id}")
    pdf_bytes = None

    try:
        try:
            pdf_bytes = download_pdf(file_key)
        except Exception as storage_err:
            logger.error(f"Error Storage: {storage_err}")
            return {"status": "error", "error": "No se pudo recuperar el documento."}

        try:
            extracted = await extract_pdf_info(pdf_bytes)
            cv_text = extracted.get("raw_text", "")
            cv_text_anon = mask_pii_data(cv_text, candidate_name)
        except Exception as parse_err:
            logger.error(f"Error PDF Parsing: {parse_err}")
            return {"status": "error", "error": "El documento PDF está corrupto."}

        try:
            prompt = PromptConfig.get_employability_report_prompt(
                candidate_data={"fullName": "el candidato"},
                soft_skills_data=games_data.get("softSkills", []),
                cv_data={"raw_text": cv_text_anon},
                job_preferences_data=prefs_data,
                employability_score=employability_score,
                level=level,
                completed_games=games_data.get("completedGames", []),
                languages_data=[],
                is_multimodal=False,
                lowest_skills_str=lowest_skills_str
            )
            
            # Pasamos explícitamente la API key validada al analizador
            api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
            analysis_result = await analyze_multimodal_report(pdf_bytes, prompt, api_key=api_key)
            
            if not isinstance(analysis_result, dict) or "error" in analysis_result:
                err_msg = analysis_result.get("error", "Fallo en inferencia de IA.")
                return {"status": "error", "error": err_msg}

        except Exception as ai_err:
            logger.exception(f"Fallo IA: {ai_err}")
            return {"status": "error", "error": "Motores de análisis no disponibles."}

        # PERSISTENCIA TRANSACCIONAL ESTRICTA (Soft-Fail DB)
        if database_engine:
            try:
                report_id = str(uuid_lib.uuid4())
                # Extraer consentimientos del payload, si vienen
                data_consent = bool(prefs_data.get('dataConsent')) if isinstance(prefs_data, dict) else False
                gdpr_consent = bool(prefs_data.get('gdprConsent')) if isinstance(prefs_data, dict) else False
                consent_version = os.getenv('PRIVACY_TEXT_VERSION') or os.getenv('PRIVACY_VERSION') or 'v1'
                consent_ts = __import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat()

                with database_engine.begin() as conn:
                    conn.execute(
                        text("INSERT IGNORE INTO users (id, email) VALUES (:id, :email)"),
                        {"id": user_id, "email": f"{user_id}@guest.evalua.te"}
                    )

                    # Intentar persistir los consentimientos en tabla independiente si existe
                    try:
                        conn.execute(
                            text("""
                                INSERT INTO user_consents (id, user_id, data_consent, gdpr_consent, consent_version, consent_ts)
                                VALUES (:id, :u, :d, :g, :v, :t)
                            """),
                            {
                                "id": str(uuid_lib.uuid4()),
                                "u": user_id,
                                "d": int(data_consent),
                                "g": int(gdpr_consent),
                                "v": consent_version,
                                "t": consent_ts,
                            }
                        )
                    except Exception as consent_err:
                        logger.debug(f"Tabla user_consents no disponible o fallo insert consent: {consent_err}")

                    conn.execute(
                        text("""
                            INSERT INTO employability_reports
                            (id, user_id, employability_score, level, report_json)
                            VALUES (:id, :u, :s, :l, :r)
                        """),
                        {
                            "id": report_id,
                            "u": user_id,
                            "s": employability_score,
                            "l": str(level),
                            "r": json.dumps(analysis_result, ensure_ascii=False)
                        }
                    )
                logger.info(f"Informe {report_id} persistido con éxito para {user_id}")
                if data_consent or gdpr_consent:
                    logger.info(f"Consentimientos registrados para {user_id}: data_consent={data_consent}, gdpr_consent={gdpr_consent}, version={consent_version} at {consent_ts}")
            except Exception as db_err:
                logger.error(f"Error de persistencia DB (Soft-Fail DB Activo): {db_err}")
                logger.warning("El informe se entregará al Frontend a pesar del fallo SQL.")

        return {"status": "completado", "report": analysis_result}

    except Exception as critical_err:
        logger.exception(f"Fallo sistémico: {critical_err}")
        return {"status": "error", "error": "Error interno crítico."}
    finally:
        if file_key:
            try:
                delete_pdf(file_key)
            except Exception as cleanup_err:
                logger.error(f"Error purga temporal: {cleanup_err}")

class WorkerSettings:
    functions = [procesar_informe_ia]
    redis_settings = RedisSettings.from_dsn(os.getenv("REDIS_URL", "redis://127.0.0.1:6379"))
    max_jobs = 10
    job_timeout = 180