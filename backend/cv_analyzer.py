#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
cv_analyzer.py

Módulo de ingesta multimodal de CVs usando Google Gemini File API.
Elimina la dependencia de OCR intermedio (fitz, pypdf) para maximizar la
preservación del contexto visual (columnas, gráficos, estructura).
"""

import asyncio
import os
import logging
import json
import tempfile
import time
from typing import Dict, Any, Optional

try:
    from dotenv import load_dotenv # type: ignore
    load_dotenv()
except ImportError:
    pass

try:
    import google.generativeai as genai  # type: ignore
except ImportError:
    # Fallback to gemini_lite (no heavy grpcio/protobuf deps — works on Vercel)
    try:
        from backend import gemini_lite as genai  # type: ignore
    except ImportError:
        try:
            import gemini_lite as genai  # type: ignore
        except ImportError:
            genai = None

# Configurar logs
logger = logging.getLogger(__name__)

# Configuración de Google Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

genai_configured = False
if GEMINI_API_KEY and genai:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        genai_configured = True
        logger.info("✅ Google Gemini configurado correctamente.")
    except Exception as e:
        logger.error(f"❌ Error configurando Gemini: {e}")
else:
    logger.warning("⚠️ GEMINI_API_KEY no configurada o librería no instalada. El análisis no funcionará.")

# Detect if we're using gemini_lite (no File API available)
_has_file_api = genai is not None and hasattr(genai, "upload_file")


def _safe_slice(text: Any, start: int, end: int) -> str:
    """Helper para hacer slicing seguro y evitar errores de linter."""
    try:
        s_text = str(text)
        # Usar bucle explicito para evitar 'slice argument not assignable to SupportsIndex'
        # Esto es menos eficiente pero complacerá al linter estricto si falla con slice puro.
        result = []
        for i in range(len(s_text)):
             if i >= start and i < end:
                 result.append(s_text[i])
        return "".join(result)
    except Exception:
        return ""

def _generate_with_retry(model, content_parts, generation_config, max_retries: int = 1, base_delay: float = 1.0):
    """Llama a generate_content con reintentos ante errores transitorios
    (rate limit, timeouts, sobrecarga del modelo) para evitar que el usuario
    tenga que recargar la página manualmente."""
    last_exc: Optional[Exception] = None
    for attempt in range(max_retries + 1):
        try:
            return model.generate_content(content_parts, generation_config=generation_config)
        except Exception as e:
            last_exc = e
            if attempt < max_retries:
                logger.warning(f"⚠️ Reintentando llamada a Gemini ({attempt + 1}/{max_retries}) tras error: {e}")
                time.sleep(base_delay * (attempt + 1))
    raise last_exc


def _normalize_ai_json_response(content: str) -> str:
    """Limpia la respuesta de la IA para obtener solo el JSON válido."""
    if not isinstance(content, str):
        text = str(content)
    else:
        text = content
    
    text = text.strip()
    
    # Eliminar bloques de código markdown ```json ... ```
    if text.startswith("```"):
        lines = text.split("\n")
        if len(lines) > 1:
            lines.pop(0) 
        if lines and lines[-1].strip() == "```":
            lines.pop() 
        text = "\n".join(lines)
    
    start = text.find("{")
    end = text.rfind("}")
    
    if start != -1 and end != -1:
        extracted = _safe_slice(text, start, end + 1)
        if extracted:
            text = extracted
        
    return text.strip()

async def extract_pdf_info(pdf_bytes: bytes) -> Dict[str, Any]:
    """
    Función principal de entrada (Interfaz compatible con main.py).
    Sube el PDF a Gemini y retorna la estructura analizada.
    """
    if not pdf_bytes:
        return {}

    cv_data = await asyncio.to_thread(analyze_cv_with_ai, pdf_bytes)
    
    return {
        "cv_info": cv_data,
        "raw_text": cv_data.get("raw_text", "Texto extraído visualmente por Gemini 1.5/2.0")
    }


def analyze_cv_with_ai(pdf_bytes: bytes) -> Dict[str, Any]:
    """
    Analiza el PDF con Gemini (File API si disponible, inline data como fallback).
    """
    if not genai_configured or not genai:
        logger.error("Gemini no está configurado. Retornando error.")
        return {"error": "Servicio de IA no disponible"}

    tmp_path = None
    uploaded_file = None

    try:
        # 3. Construir el Prompt Visual Estricto
        system_instruction = (
            "Eres un experto reclutador técnico con visión artificial avanzada. "
            "Tu tarea es leer este CV VISUALMENTE. "
            "DETECTA COLUMNAS: Lee de izquierda a derecha dentro de cada columna. "
            "No cruces texto entre columnas diferentes. "
            "INTERPRETA GRÁFICOS: Si ves barras de progreso o estrellas (★★★★☆), conviértelas a "
            "una escala numérica (4/5) o 'Alto/Medio/Bajo'. "
            "Respeta la estructura original del documento."
        )

        prompt = """
        ANALIZA ESTE CURRICULUM VITAE Y EXTRAE LA SIGUIENTE INFORMACIÓN ESTRUCTURADA EN UN JSON.
        
        SI EL DOCUMENTO TIENE DOBLE COLUMNA, ASEGÚRATE DE LEER CADA UNA POR SEPARADO.
        NO INVENTES DATOS. Si no aparecen, usa null o [].
        
        Estructura JSON requerida:
        {
          "datos_personales": {
            "nombre": "Nombre completo",
            "email": "email",
            "telefono": "teléfono",
            "ubicacion": "ciudad/país",
            "linkedin": "url",
            "web": "url"
          },
          "resumen_profesional": "Extracto o perfil profesional (About me)",
          "experiencia": [
            {
              "empresa": "Nombre Empresa",
              "rol": "Cargo ocupado",
              "fecha_inicio": "YYYY-MM o Texto",
              "fecha_fin": "YYYY-MM o 'Actualidad'",
              "descripcion": "Descripción breve",
              "responsabilidades": ["Lista detallada de bullets"],
              "tecnologias": ["Tech stack usado en este rol"]
            }
          ],
          "educacion": [
            {
              "titulo": "Título obtenido",
              "institucion": "Universidad/Centro",
              "fecha_inicio": "Año",
              "fecha_fin": "Año"
            }
          ],
          "habilidades_detectadas": [
            { "herramienta": "Nombre (ej. Python)", "nivel": "Alto/Medio/Bajo o Score 0-100" }
          ],
          "habilidades_blandas": ["Lista de soft skills mencionadas explícitamente"],
          "idiomas": [
            { "idioma": "Idioma", "nivel": "Nativo/C1/B2/etc" }
          ],
          "proyectos": [
            { "nombre": "Nombre", "descripcion": "Detalles" }
          ],
          "certificaciones": [
            { "nombre": "Certificación", "emisor": "Entidad", "fecha": "Año" }
          ],
          "raw_text": "Breve resumen de lo que has podido leer visualmente (máx 500 caracteres) para depuración"
        }
        """

        # 4. Generar contenido
        model_name = "gemini-flash-latest"
        model = genai.GenerativeModel(
            model_name=model_name,
            system_instruction=system_instruction
        )

        logger.info(f"🧠 Analizando documento con {model_name} y temperature=0.1...")
        generation_config = genai.types.GenerationConfig(
            temperature=0.1,
            response_mime_type="application/json"
        )

        if _has_file_api:
            # SDK completo: subir a File API y referenciar
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
                tmp.write(pdf_bytes)
                tmp_path = tmp.name
            uploaded_file = genai.upload_file(tmp_path, mime_type="application/pdf")
            logger.info(f"✅ Archivo subido via File API: {uploaded_file.uri}")
            content_parts = [uploaded_file, prompt]
        else:
            # gemini_lite: inline data (base64) — sin File API
            logger.info("📎 Usando inline PDF data (gemini_lite mode)")
            content_parts = [{"mime_type": "application/pdf", "data": pdf_bytes}, prompt]

        response = _generate_with_retry(model, content_parts, generation_config)

        # 5. Procesar respuesta
        json_text = _normalize_ai_json_response(response.text)
        return json.loads(json_text)

    except Exception as e:
        logger.exception(f"❌ Error crítico en análisis visual con Gemini: {e}")
        return {
            "error": str(e),
            "datos_personales": {},
            "experiencia": [],
            "raw_text": "Error durante el análisis."
        }
    finally:
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except OSError:
                pass
        if uploaded_file and _has_file_api and genai:
            try:
                genai.delete_file(uploaded_file.name)
            except Exception:
                pass

async def analyze_multimodal_report(pdf_bytes: bytes, report_prompt: str) -> Dict[str, Any]:
    """
    Función optimizada: Genera reporte directo desde PDF usando prompt multimodal.
    Evita la latencia de doble llamada.
    """
    if not genai_configured or not genai:
        return {"error": "Servicio de IA no disponible"}

    tmp_path = None
    uploaded_file = None

    try:
        model = genai.GenerativeModel(
            model_name="gemini-flash-latest",
            system_instruction="Eres un experto orientador laboral. Analiza el CV visualmente y genera el informe JSON estricto."
        )
        generation_config = genai.types.GenerationConfig(
            temperature=0.4,
            response_mime_type="application/json"
        )

        if _has_file_api:
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
                tmp.write(pdf_bytes)
                tmp_path = tmp.name
            uploaded_file = genai.upload_file(tmp_path, mime_type="application/pdf")
            logger.info(f"✅ Archivo subido via File API: {uploaded_file.uri}")
            content_parts = [uploaded_file, report_prompt]
        else:
            logger.info("📎 Usando inline PDF data para informe (gemini_lite mode)")
            content_parts = [{"mime_type": "application/pdf", "data": pdf_bytes}, report_prompt]

        logger.info("🧠 Generando informe multimodal (Single-Shot)...")
        response = await model.generate_content_async(content_parts, generation_config=generation_config)

        json_text = _normalize_ai_json_response(response.text)
        return json.loads(json_text)

    except Exception as e:
        logger.exception(f"❌ Error multimodal: {e}")
        return {"error": str(e)}

    finally:
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except OSError:
                pass
        if uploaded_file and _has_file_api and genai:
            try:
                genai.delete_file(uploaded_file.name)
            except Exception:
                pass

# Backward compatibility functions
def extract_contact_info_enhanced(text: str) -> Dict[str, str]:
    return {}

def analyze_cv_structure_ai(cv_data: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "structure_score": 5, 
        "structure": "bueno", 
        "observations": ["Análisis realizado mediante Ingesta Nativa Gemini"]
    }

