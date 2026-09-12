# backend/report_engine.py
"""
Motor de generación de informes de empleabilidad.

Sustituye al antiguo worker.py (ARQ + Redis). En un entorno serverless
(Vercel Functions) no existe un proceso de fondo persistente que consuma
una cola, así que el análisis se ejecuta de forma síncrona dentro de la
misma invocación de /api/analyze.
"""
import json
import logging
import os
import uuid as uuid_lib
import datetime
from typing import Any, Dict

from sqlalchemy import text

try:
    from backend.cv_analyzer import extract_pdf_info, analyze_multimodal_report
    from backend.prompt_config import PromptConfig
    from backend.pii_masking import mask_pii_data
    from backend.deterministic_report import generate_deterministic_report
except ImportError:
    from cv_analyzer import extract_pdf_info, analyze_multimodal_report
    from prompt_config import PromptConfig
    from pii_masking import mask_pii_data
    from deterministic_report import generate_deterministic_report

logger = logging.getLogger("report_engine")

# Por defecto el informe se genera SOLO con automatización determinista (sin
# IA generativa): no depende de cuotas ni disponibilidad de Gemini/terceros,
# y responde al instante. Poner ENABLE_AI_REPORT=true reactiva el intento de
# IA como primera opción (con el motor determinista como respaldo si falla).
def _ai_report_enabled() -> bool:
    return (os.getenv("ENABLE_AI_REPORT") or "").strip().lower() in ("1", "true", "yes", "on")


async def run_employability_analysis(
    pdf_bytes: bytes,
    user_id: str,
    games_data: dict,
    prefs_data: dict,
    employability_score: int,
    level: str,
    lowest_skills_str: str,
    candidate_name: str,
    database_engine=None,
) -> Dict[str, Any]:
    """Ejecuta el análisis de IA sobre el CV y devuelve el informe completo.

    Equivalente síncrono de `procesar_informe_ia` (antiguo worker de ARQ).
    """
    try:
        analysis_result = None
        used_ai = False

        if _ai_report_enabled():
            try:
                extracted = await extract_pdf_info(pdf_bytes)
                cv_text = extracted.get("raw_text", "")
                cv_text_anon = mask_pii_data(cv_text, candidate_name)

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
                    lowest_skills_str=lowest_skills_str,
                )

                api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
                ai_result = await analyze_multimodal_report(pdf_bytes, prompt, api_key=api_key)

                if isinstance(ai_result, dict) and "error" not in ai_result:
                    analysis_result = ai_result
                    used_ai = True
                else:
                    logger.warning(
                        f"IA no disponible ({(ai_result or {}).get('error') if isinstance(ai_result, dict) else ai_result}); "
                        "generando informe con el motor determinista (sin IA)."
                    )
            except Exception as ai_err:
                logger.warning(f"Fallo IA, se usa el motor determinista (sin IA): {ai_err}")

        if analysis_result is None:
            try:
                analysis_result = generate_deterministic_report(
                    pdf_bytes=pdf_bytes,
                    games_data=games_data,
                    prefs_data=prefs_data,
                    employability_score=employability_score,
                    candidate_name=candidate_name,
                )
            except Exception as det_err:
                logger.exception(f"Fallo crítico en el motor determinista: {det_err}")
                return {"status": "error", "error": "Error interno crítico."}

        logger.info(f"Informe generado con motor {'IA (Gemini)' if used_ai else 'determinista (sin IA)'} para {user_id}")

        # PERSISTENCIA TRANSACCIONAL ESTRICTA (Soft-Fail DB)
        if database_engine:
            try:
                report_id = str(uuid_lib.uuid4())
                data_consent = bool(prefs_data.get("dataConsent")) if isinstance(prefs_data, dict) else False
                gdpr_consent = bool(prefs_data.get("gdprConsent")) if isinstance(prefs_data, dict) else False
                consent_version = os.getenv("PRIVACY_TEXT_VERSION") or os.getenv("PRIVACY_VERSION") or "v1"
                consent_ts = datetime.datetime.now(datetime.timezone.utc).isoformat()

                with database_engine.begin() as conn:
                    conn.execute(
                        text("INSERT IGNORE INTO users (id, email) VALUES (:id, :email)"),
                        {"id": user_id, "email": f"{user_id}@guest.evalua.te"},
                    )

                    try:
                        conn.execute(
                            text(
                                """
                                INSERT INTO user_consents (id, user_id, data_consent, gdpr_consent, consent_version, consent_ts)
                                VALUES (:id, :u, :d, :g, :v, :t)
                                """
                            ),
                            {
                                "id": str(uuid_lib.uuid4()),
                                "u": user_id,
                                "d": int(data_consent),
                                "g": int(gdpr_consent),
                                "v": consent_version,
                                "t": consent_ts,
                            },
                        )
                    except Exception as consent_err:
                        logger.debug(f"Tabla user_consents no disponible o fallo insert consent: {consent_err}")

                    conn.execute(
                        text(
                            """
                            INSERT INTO employability_reports
                            (id, user_id, employability_score, level, report_json)
                            VALUES (:id, :u, :s, :l, :r)
                            """
                        ),
                        {
                            "id": report_id,
                            "u": user_id,
                            "s": employability_score,
                            "l": str(level),
                            "r": json.dumps(analysis_result, ensure_ascii=False),
                        },
                    )
                logger.info(f"Informe {report_id} persistido con éxito para {user_id}")
            except Exception as db_err:
                logger.error(f"Error de persistencia DB (Soft-Fail DB Activo): {db_err}")
                logger.warning("El informe se entregará al Frontend a pesar del fallo SQL.")

        return {"status": "completado", "report": analysis_result}

    except Exception as critical_err:
        logger.exception(f"Fallo sistémico: {critical_err}")
        return {"status": "error", "error": "Error interno crítico."}
