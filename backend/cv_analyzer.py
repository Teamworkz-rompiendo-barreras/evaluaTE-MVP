#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo de ingesta multimodal de CVs usando Google Gemini.
ACTUALIZACIÓN B2B (V17.0 MAP-REDUCE COGNITIVO CON ESTADO COMPARTIDO):
- Evasión total del límite de 8192 Output Tokens mediante Chunking Concurrente.
- Fase 1: Generación del Modelo Mental (Diagnóstico Interno Oculto).
- Fase 2: Inyección de la Fuente de la Verdad en 3 Chunks paralelos.
- Purga estricta de datos privados antes de enviar al cliente (GDPR).
"""
import asyncio
import logging
import json
import os
import random
from typing import Dict, Any
from pydantic import BaseModel
import requests

try:
    from backend.env_loader import get_gemini_api_keys, load_backend_env
except ImportError:
    from env_loader import get_gemini_api_keys, load_backend_env

load_backend_env()

try:
    from google import genai
    from google.genai import types
except ImportError:
    genai = None
    types = None

try:
    import json_repair
except ImportError:
    json_repair = None

try:
    from backend.new_report_schema import (
        DiagnosticoInternoOculto, Chunk1Base, Chunk2Competencias, Chunk3Accion
    )
except ImportError:
    from new_report_schema import (
        DiagnosticoInternoOculto, Chunk1Base, Chunk2Competencias, Chunk3Accion
    )

logger = logging.getLogger(__name__)
genai_configured = genai is not None

RATE_LIMIT_BACKOFF_SECONDS = (0.25, 0.75)
MAX_RETRIES_PER_MODEL = 1
STAGGER_DELAY_SECONDS = (0.0, 0.5, 1.0)


def _short_key(key: str | None) -> str:
    if not key:
        return "(sin-key)"
    return f"{key[:8]}...{key[-4:]}" if len(key) > 12 else key[:8]

SUPPORTED_GEMINI_MODELS = [
    "gemini-2.5-flash",
    "gemini-2.0-flash",
    "gemini-1.5-flash",
    "gemini-1.5-pro",
]


def _sanitize_model_name(model_name: str | None) -> str | None:
    if not model_name:
        return None
    candidate = str(model_name).strip().strip('"').strip("'")
    if candidate.startswith("models/"):
        candidate = candidate.split("/", 1)[1]
    return candidate if candidate in SUPPORTED_GEMINI_MODELS else None


_primary_model = _sanitize_model_name(os.getenv("GEMINI_PRIMARY_MODEL", "gemini-2.5-flash")) or "gemini-2.5-flash"
_preview_model = _sanitize_model_name(os.getenv("GEMINI_PREVIEW_MODEL")) or "gemini-2.0-flash"

fallback_candidates = [
    _primary_model,
    _preview_model,
    "gemini-2.5-flash",
    "gemini-2.0-flash",
    "gemini-1.5-flash",
    "gemini-1.5-pro",
]
FALLBACK_MODELS = []
for model_name in fallback_candidates:
    cleaned = _sanitize_model_name(model_name)
    if cleaned and cleaned not in FALLBACK_MODELS:
        FALLBACK_MODELS.append(cleaned)

if not FALLBACK_MODELS:
    FALLBACK_MODELS = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash"]

if os.getenv("GEMINI_PREVIEW_MODEL") and _sanitize_model_name(os.getenv("GEMINI_PREVIEW_MODEL")) is None:
    logger.warning(
        "GEMINI_PREVIEW_MODEL no es un modelo Gemini soportado; se ignora y se usan los modelos válidos por defecto. "
        "Valor actual: %s",
        os.getenv("GEMINI_PREVIEW_MODEL"),
    )

def _default_cv_analysis() -> dict:
    return {
        "resumen": "El CV aporta una base profesional válida pero necesita mayor concreción de resultados, liderazgo y posicionamiento para mejorar su visibilidad en el mercado.",
        "experiencia": [
            "Experiencia profesional con potencial de crecimiento y mejor articulación de resultados.",
            "Se recomienda cuantificar impacto y logros medibles en cada rol.",
        ],
        "formacion": [
            "Formación relevante para el perfil, aunque puede reforzarse con especialización sectorial o técnica.",
        ],
        "idiomas": ["No se especifican idiomas clave en el documento."],
        "software": ["Herramientas digitales generales no detalladas de forma específica."],
        "valoraciones": {
            "formato": 3,
            "claridad": 3,
            "coherencia": 3,
            "info_clave": 3,
            "ortografia": 3,
        },
        "puntos_fuertes": [
            "Perfil con recorrido profesional y potencial de adaptación.",
            "Base sólida para construir una narrativa de valor más potente.",
        ],
        "aspectos_mejorar": [
            "Necesita mayor concreción de logros y resultados cuantificados.",
            "Debe reforzar la estructura y la claridad para optimizar ATS y revisión por reclutadores.",
        ],
        "ats_compatibilidad": 60,
        "ats_explicacion": "El documento tiene potencial, pero requiere más claridad, estructura y evidencia de resultados para mejorar la compatibilidad con ATS y la lectura del reclutador.",
    }


def _enforce_business_rules(report_data: dict) -> dict:
    """Validador determinista: Aplica reglas de negocio matemáticas sobre el JSON ensamblado."""
    try:
        analisis_cv = report_data.get("analisis_cv") if isinstance(report_data.get("analisis_cv"), dict) else {}
        if not analisis_cv:
            analisis_cv = _default_cv_analysis()

        valoraciones_base = {"formato": 4, "claridad": 4, "coherencia": 3, "info_clave": 4, "ortografia": 5}
        valoraciones = analisis_cv.get("valoraciones", valoraciones_base)
        if not isinstance(valoraciones, dict):
            valoraciones = valoraciones_base
        for key, default_value in valoraciones_base.items():
            valoraciones.setdefault(key, default_value)

        analisis_cv.setdefault("resumen", _default_cv_analysis()["resumen"])
        analisis_cv.setdefault("experiencia", _default_cv_analysis()["experiencia"])
        analisis_cv.setdefault("formacion", _default_cv_analysis()["formacion"])
        analisis_cv.setdefault("idiomas", _default_cv_analysis()["idiomas"])
        analisis_cv.setdefault("software", _default_cv_analysis()["software"])
        analisis_cv.setdefault("puntos_fuertes", _default_cv_analysis()["puntos_fuertes"])
        analisis_cv.setdefault("aspectos_mejorar", _default_cv_analysis()["aspectos_mejorar"])
        analisis_cv.setdefault("ats_compatibilidad", 60)
        analisis_cv.setdefault("ats_explicacion", _default_cv_analysis()["ats_explicacion"])
        analisis_cv["valoraciones"] = valoraciones

        aspectos = " ".join(analisis_cv.get("aspectos_mejorar", []) or []).lower()
        if any(keyword in aspectos for keyword in ["ortograf", "errat", "tipográfic", "escribir", "tildes", "indesing", "ilustrator"]):
            valoraciones["ortografia"] = 2
        if any(keyword in aspectos for keyword in ["métric", "kpi", "cuantificable", "numéric", "ausencia de datos"]):
            valoraciones["info_clave"] = 2

        if not analisis_cv.get("valoraciones"):
            analisis_cv["valoraciones"] = valoraciones_base

        analisis_cv["valoraciones"] = valoraciones
        report_data["analisis_cv"] = analisis_cv
    except Exception as e:
        logger.warning(f"Error aplicando reglas de negocio matemáticas: {e}")
        report_data.setdefault("analisis_cv", _default_cv_analysis())
    return report_data


def _extract_json_payload(raw_text: str):
    cleaned = raw_text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.replace("```json", "").replace("```", "").strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start != -1 and end != -1 and end > start:
            candidate = cleaned[start:end+1]
            return json.loads(candidate)
        raise


async def _generate_chunk_via_groq(content_parts: list, system_instruction: str, chunk_name: str, schema: Any = None):
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("No hay GROQ_API_KEY configurada para fallback")

    prompt_text = "\n".join(
        part if isinstance(part, str) else "<PDF documento anexado>"
        for part in content_parts
        if isinstance(part, str) or hasattr(part, "mime_type")
    )
    payload = {
        "model": os.getenv("GROQ_MODEL", "llama-3.1-8b-instant"),
        "messages": [
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": prompt_text or system_instruction}
        ],
        "temperature": 0.2,
        "max_tokens": 8192,
    }

    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json=payload,
        timeout=90,
    )

    if response.status_code != 200:
        text = response.text[:500]
        raise RuntimeError(f"Groq fallback error {response.status_code}: {text}")

    data = response.json()
    content = data["choices"][0]["message"]["content"]
    logger.warning(f"[{chunk_name}] Generado con fallback de Groq.")
    return _extract_json_payload(content)


async def _generate_chunk_async(
    content_parts: list, 
    system_instruction: str, 
    schema: Any, 
    chunk_name: str, 
    api_key: str = None, 
    retries_per_model: int = MAX_RETRIES_PER_MODEL
) -> Dict[str, Any]:
    """Generador aislado para un fragmento del informe con Jitter anti-colisión y rotación de claves."""
    if not api_key:
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_KEY_1")
    if not api_key:
        load_backend_env()
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_KEY_1")

    last_exc = None
    configured_keys = []
    if api_key:
        configured_keys.append(api_key.strip())
    for key in get_gemini_api_keys():
        if key not in configured_keys:
            configured_keys.append(key)

    if not configured_keys:
        configured_keys = [None]

    logger.info(f"[{chunk_name}] Iniciando rotación de Gemini. Claves probadas: {[ _short_key(k) for k in configured_keys ]}. Modelos: {FALLBACK_MODELS}")

    for key_index, active_key in enumerate(configured_keys):
        key_label = _short_key(active_key)
        logger.info(f"[{chunk_name}] Probando Gemini con clave #{key_index + 1}: {key_label}")
        client = genai.Client(api_key=active_key) if active_key else genai.Client()
        for idx, model_name in enumerate(FALLBACK_MODELS):
            for attempt in range(retries_per_model + 1):
                try:
                    if key_index > 0 and attempt == 0:
                        logger.warning(f"[{chunk_name}] Rotando clave de Gemini: índice {key_index} -> {key_label}")
                    if idx > 0 and attempt == 0:
                        logger.warning(f"[{chunk_name}] Rotando a modelo de respaldo: {model_name}")

                    config = types.GenerateContentConfig(
                        system_instruction=system_instruction,
                        temperature=0.25,
                        response_mime_type="application/json",
                        response_schema=schema,
                        max_output_tokens=8192
                    )
                    
                    response = await client.aio.models.generate_content(
                        model=model_name,
                        contents=content_parts,
                        config=config
                    )
                    
                    if hasattr(response, 'parsed') and response.parsed is not None:
                        logger.info(f"[{chunk_name}] Generado exitosamente vía Pydantic SDK.")
                        return response.parsed.model_dump()
                    
                    if not response.text:
                        raise ValueError("Respuesta de API vacía.")
                    
                    text_response = response.text.replace("```json", "").replace("```", "").strip()
                    
                    try:
                        return json.loads(text_response)
                    except json.JSONDecodeError as jde:
                        if json_repair:
                            decoded = json_repair.loads(text_response)
                            if isinstance(decoded, dict):
                                logger.info(f"[{chunk_name}] Recuperado vía json_repair.")
                                return decoded
                        raise jde

                except Exception as e:
                    last_exc = e
                    error_msg = str(e).lower()
                    if "429" in error_msg or "quota" in error_msg or "503" in error_msg:
                        sleep_time = random.uniform(*RATE_LIMIT_BACKOFF_SECONDS)
                        logger.warning(f"[{chunk_name}] Cuota en {model_name} con clave {key_index}. Reintento ágil en {sleep_time:.2f}s... (Intento {attempt+1}/{retries_per_model})")
                        await asyncio.sleep(sleep_time)
                        continue
                    elif "404" in error_msg:
                        logger.warning(f"[{chunk_name}] Modelo {model_name} no disponible. Saltando.")
                        break
                    else:
                        if attempt < retries_per_model:
                            await asyncio.sleep(2)
                        else:
                            break
        logger.warning(f"[{chunk_name}] Se agotaron intento con la clave {key_index}. Probando siguiente clave.")

    logger.warning(f"[{chunk_name}] Todas las claves de Gemini fallaron; intentando fallback a Groq con modelo {os.getenv('GROQ_MODEL', 'llama-3.1-8b-instant')}")
    try:
        return await _generate_chunk_via_groq(content_parts, system_instruction, chunk_name, schema)
    except Exception as groq_exc:
        logger.exception(f"[{chunk_name}] Fallback a Groq también falló: {groq_exc}")
        raise last_exc or groq_exc

async def _generate_chunk_with_delay(delay: float, *args, **kwargs) -> Dict[str, Any]:
    """Envoltorio para escalonar (stagger) el lanzamiento asíncrono y evitar cuellos de botella."""
    if delay > 0:
        await asyncio.sleep(delay)
    return await _generate_chunk_async(*args, **kwargs)

async def extract_pdf_info(pdf_bytes: bytes) -> Dict[str, Any]:
    if not pdf_bytes: return {}
    return {"raw_text": "Texto extraído del documento PDF para su análisis."}

async def analyze_multimodal_report(pdf_bytes: bytes, report_prompt: str, api_key: str = None) -> Dict[str, Any]:
    if not genai_configured and not api_key:
        return {"error": "Falta API Key o paquete google-genai."}
    
    system_instruction_base = "Eres un Mentor Ejecutivo B2B y Consultor de Talento Senior. Tu tono es profesional, analítico, inspirador y constructivo. Ejerces un escrutinio lógico implacable. NUNCA uses texto genérico."
    logger.info(f"Iniciando arquitectura MAP-REDUCE COGNITIVO (SDK V2 con {FALLBACK_MODELS[0]})...")
    
    content_parts = [
        types.Part.from_bytes(data=pdf_bytes, mime_type="application/pdf"),
        report_prompt
    ]
    
    try:
        # FASE 1: Construcción del Modelo Mental (Scratchpad)
        logger.info("[Fase 1] Generando Diagnóstico Interno Oculto (Cadena de Pensamiento)...")
        diagnostico_crudo = await _generate_chunk_async(
            content_parts=content_parts,
            system_instruction=system_instruction_base + " OBLIGATORIO: Analiza la viabilidad del perfil y construye tu hipótesis interna. Piensa paso a paso.",
            schema=DiagnosticoInternoOculto,
            chunk_name="DiagnosticoMental",
            api_key=api_key
        )
        
        # FASE 2: Inyección de la Fuente de la Verdad a los Chunks Paralelos
        diagnostico_str = json.dumps(diagnostico_crudo, ensure_ascii=False)
        logger.info("[Fase 1] Diagnóstico completado. Inyectando como fuente de la verdad innegociable.")
        
        system_instruction_chunks = (
            system_instruction_base + 
            "\n\n### DIAGNÓSTICO MAESTRO DEL CANDIDATO (FUENTE DE LA VERDAD OBLIGATORIA) ###\n"
            "Utiliza ESTRICTAMENTE este análisis previo para redactar tu sección. No lo contradigas en ningún punto:\n"
            f"{diagnostico_str}"
        )
        
        # FASE 3: Generación Concurrente Escalonada (Staggered Starts)
        logger.info("[Fase 2] Disparando Chunks Concurrentes...")
        res_base, res_comp, res_acc = await asyncio.gather(
            _generate_chunk_with_delay(STAGGER_DELAY_SECONDS[0], content_parts, system_instruction_chunks, Chunk1Base, "Chunk_Base", api_key),
            _generate_chunk_with_delay(STAGGER_DELAY_SECONDS[1], content_parts, system_instruction_chunks, Chunk2Competencias, "Chunk_Competencias", api_key),
            _generate_chunk_with_delay(STAGGER_DELAY_SECONDS[2], content_parts, system_instruction_chunks, Chunk3Accion, "Chunk_Accion", api_key)
        )
        
        # FASE 4: Ensamblaje y Privacidad
        # "diagnostico_interno_oculto" se queda atrás por diseño, jamás cruza al frontend
        informe_completo = {**res_base, **res_comp, **res_acc}
        informe_validado = _enforce_business_rules(informe_completo)
        
        logger.info("Generación de informe B2B completada y ensamblada con éxito.")
        return informe_validado
        
    except Exception as e:
        logger.exception(f"Fallo en la orquestación Map-Reduce: {e}")
        return {
            "error": "El servidor de IA experimenta alta demanda temporal y el análisis ha sido truncado. Por favor, reinténtalo en unos minutos."
        }