# backend/generate_report.py
import os
import json
import httpx
import logging
from typing import Any, Dict

logger = logging.getLogger("evaluador-backend")

AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")  # p.ej. https://<tu-recurso>.openai.azure.com
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4.1")  # tu deployment name
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-10-21")

if not AZURE_OPENAI_ENDPOINT or not AZURE_OPENAI_API_KEY:
    logger.warning("⚠️ Falta configuración de Azure OpenAI (AZURE_OPENAI_ENDPOINT / AZURE_OPENAI_API_KEY)")

# Instrucciones al modelo para devolver JSON estructurado estable
SYSTEM_PROMPT = """Eres un analista de empleabilidad. Devuelve SIEMPRE un JSON estricto con las siguientes claves:
{
  "summary": string,
  "personal_data": { "name": string|null, "location": string|null, "email": string|null, "phone": string|null, "linkedin": string|null },
  "profile_summary": string,
  "cv_summary": string,
  "strengths": [string],
  "improvement_areas": [string],
  "cv_analysis": {
    "format": string,
    "clarity": string,
    "coherence": string,
    "key_info": string,
    "spelling": string,
    "stars": { "formato": number, "claridad": number, "coherencia": number, "informacion_clave": number, "ortografia": number }
  },
  "ideal_work_environment": [string],
  "suggested_roles": [ { "role": string, "reason": string, "seniority": string, "remote_viable": boolean } ],
  "action_plan": { "short_term": [string], "mid_term": [string], "long_term": [string] },
  "job_search_advice": [string],
  "useful_tools": { "productivity": [string], "job_search": [string], "learning": [string], "accessibility": [string] },
  "completed_games": [string],
  "final_message": string
}
Nada de texto fuera del JSON. Asegúrate de que los valores de 'stars' estén entre 1 y 5. Si falta información del CV, indícalo, pero no inventes datos.
"""

def generar_informe(prompt: str) -> Dict[str, Any]:
    """
    Llama a Azure OpenAI (Chat Completions) y devuelve un dict con el informe JSON.
    """
    if not AZURE_OPENAI_ENDPOINT or not AZURE_OPENAI_API_KEY:
        # Fallback seguro: informe mínimo
        logger.warning("Azure OpenAI no configurado. Se devuelve informe mínimo.")
        return {
            "summary": "No hay configuración de OpenAI. Informe mínimo.",
            "personal_data": {},
            "profile_summary": "",
            "cv_summary": "CV no analizado.",
            "strengths": [],
            "improvement_areas": [],
            "cv_analysis": {
                "format": "",
                "clarity": "",
                "coherence": "",
                "key_info": "",
                "spelling": "",
                "stars": {"formato":3,"claridad":3,"coherencia":3,"informacion_clave":2,"ortografia":3}
            },
            "ideal_work_environment": [],
            "suggested_roles": [],
            "action_plan": {"short_term":[],"mid_term":[],"long_term":[]},
            "job_search_advice": [],
            "useful_tools": {"productivity":[],"job_search":[],"learning":[],"accessibility":[]},
            "completed_games": [],
            "final_message": ""
        }

    url = f"{AZURE_OPENAI_ENDPOINT.rstrip('/')}/openai/deployments/{AZURE_OPENAI_DEPLOYMENT}/chat/completions"
    params = {"api-version": AZURE_OPENAI_API_VERSION}

    payload = {
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.2,
        "max_tokens": 1800,
        "response_format": { "type": "json_object" }
    }

    headers = {
        "Content-Type": "application/json",
        "api-key": AZURE_OPENAI_API_KEY,
    }

    logger.info("cv: openai_request")
    with httpx.Client(timeout=60) as client:
        r = client.post(url, params=params, headers=headers, json=payload)
        r.raise_for_status()
        data = r.json()
    logger.info("cv: openai_response")

    # Extraer el JSON del contenido del primer choice
    content = data["choices"][0]["message"]["content"]
    try:
        parsed = json.loads(content)
    except Exception:
        # Si por algún motivo no viene JSON puro, encapsúlalo
        parsed = {"summary": content}

    return parsed
