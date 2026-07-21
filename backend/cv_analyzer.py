# backend/cv_analyzer.py
# -*- coding: utf-8 -*-
import re
import logging
import os
import io
import sys
import json
import asyncio
from typing import Dict, Any
from fastapi import UploadFile
from google import genai
from google.genai import types
import fitz  # PyMuPDF
import docx  # python-docx
import pytesseract
from PIL import Image

if sys.platform == "win32":
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

os.environ["TESSDATA_PREFIX"] = r'C:\Program Files\Tesseract-OCR\tessdata'

logger = logging.getLogger(__name__)

EMAIL_REGEX = re.compile(r"[\w\.-]+@[\w\.-]+\.\w+")
PHONE_REGEX = re.compile(r"(\+?\d{1,3}[\s-]?)?\(?\d{2,3}\)?[\s.-]?\d{3}[\s.-]?\d{3,4}")
DNI_REGEX = re.compile(r"\b\d{8}[A-Z]\b", re.IGNORECASE)

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

def _extract_from_pdf(pdf_bytes: bytes) -> str:
    text = ""
    with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
        for page in doc:
            text += page.get_text()
            
    if len(text.strip()) < 50:
        logger.info("PDF escaneado detectado. Iniciando OCR...")
        text = ""
        with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
            for page in doc:
                pix = page.get_pixmap(dpi=150)
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                text += pytesseract.image_to_string(img, lang="spa") + "\n"
    return text

def _extract_from_docx(docx_bytes: bytes) -> str:
    text = ""
    doc = docx.Document(io.BytesIO(docx_bytes))
    for para in doc.paragraphs:
        text += para.text + "\n"
    return text

def _extract_from_image(image_bytes: bytes) -> str:
    img = Image.open(io.BytesIO(image_bytes))
    text = pytesseract.image_to_string(img, lang="spa")
    return text

async def extract_and_anonymize_cv(cv_file: UploadFile) -> str:
    try:
        file_bytes = await cv_file.read()
        if not file_bytes:
            return ""
        
        filename = (cv_file.filename or "").lower()
        text = ""
        
        if filename.endswith(".pdf"):
            text = _extract_from_pdf(file_bytes)
        elif filename.endswith((".docx", ".doc")):
            text = _extract_from_docx(file_bytes)
        elif filename.endswith((".jpg", ".jpeg", ".png")):
            text = _extract_from_image(file_bytes)
        else:
            text = file_bytes.decode('utf-8', errors='ignore')
            
        if not text.strip():
            logger.warning("No se detectaron caracteres legibles tras el OCR.")
            return ""

        text = EMAIL_REGEX.sub("[EMAIL_PROTEGIDO]", text)
        text = PHONE_REGEX.sub("[TELEFONO_PROTEGIDO]", text)
        text = DNI_REGEX.sub("[ID_PROTEGIDO]", text)
        
        return text
    except Exception as e:
        logger.error(f"Error procesando documento local: {e}")
        return ""

async def analyze_multimodal_report(safe_prompt: str) -> Dict[str, Any]:
    # FIX ARQUITECTURA: Algoritmo de Exponential Backoff (4 intentos, tiempo progresivo)
    max_retries = 4 
    base_delay = 3

    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=safe_prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.1
                )
            )

            raw_text = response.text
            if not raw_text:
                if attempt < max_retries - 1:
                    sleep_time = base_delay * (2 ** attempt)
                    logger.warning(f"Respuesta vacía. Retroceso exponencial de {sleep_time}s ({attempt + 1}/{max_retries})...")
                    await asyncio.sleep(sleep_time)
                    continue
                return {"success": False, "error": "Respuesta vacía del LLM tras varios intentos."}

            try:
                parsed_data = json.loads(raw_text)
                return {"success": True, "data": parsed_data}
            except json.JSONDecodeError as e:
                logger.error(f"Fallo al decodificar JSON de Gemini: {e}")
                clean_text = raw_text.replace("```json", "").replace("```", "").strip()
                try:
                    parsed_data = json.loads(clean_text)
                    return {"success": True, "data": parsed_data}
                except Exception:
                    return {"success": False, "error": "Formato JSON ilegible."}
                    
        except Exception as e:
            error_msg = str(e).lower()
            logger.warning(f"API de Google saturada o caída (Intento {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                sleep_time = base_delay * (2 ** attempt) # Secuencia: 3s, 6s, 12s...
                logger.info(f"Aplicando retroceso exponencial. Esperando en la sombra {sleep_time} segundos...")
                await asyncio.sleep(sleep_time) 
            else:
                logger.error(f"Error crítico en IA tras {max_retries} intentos. Abortando.")
                # Extraemos el mensaje real para pasarlo al frontend
                if "503" in error_msg or "unavailable" in error_msg or "high demand" in error_msg:
                    return {"success": False, "error": "Los servidores de IA están saturados por alta demanda mundial. Por favor, espera 1 minuto y vuelve a intentarlo."}
                return {"success": False, "error": "El servidor de inteligencia artificial rechazó la conexión. Verifica tu conectividad o inténtalo más tarde."}

    return {"success": False, "error": "Fallo desconocido en el motor de IA."}