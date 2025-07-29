#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import fitz  # PyMuPDF
import re
import json
import sys
import io
import os
from typing import Dict, List, Any, Optional
from openai import AzureOpenAI
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración de Azure OpenAI
API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT")
API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")

# Cliente de Azure OpenAI
client = None
if all([API_KEY, ENDPOINT, DEPLOYMENT, API_VERSION]):
    try:
        client = AzureOpenAI(
            api_key=API_KEY,
            api_version=API_VERSION,
            azure_endpoint=ENDPOINT,
            timeout=300.0
        )
    except Exception as e:
        print(f"⚠️ Error configurando Azure OpenAI: {e}")

# Importaciones para OCR
try:
    import pytesseract
    from PIL import Image
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False
    print("⚠️ OCR no disponible. Instala pytesseract y Pillow para mejor soporte de PDFs escaneados.")

def extract_text_with_advanced_ocr(pdf_buffer: bytes) -> str:
    """
    Extrae texto de un PDF usando OCR avanzado para todas las páginas
    """
    try:
        doc = fitz.open(stream=pdf_buffer, filetype="pdf")
        text = ""
        
        # Procesar todas las páginas
        for page_num in range(len(doc)):
            page = doc[page_num]
            
            # Intentar extraer texto normal primero
            page_text = page.get_text("text")
            
            # Si hay texto suficiente, usarlo
            if len(page_text.strip()) > 20:
                text += page_text + "\n"
            elif OCR_AVAILABLE:
                # Usar OCR para páginas sin texto o con poco texto
                try:
                    # Obtener imagen de alta resolución
                    zoom = 2.0  # Aumentar resolución para mejor OCR
                    mat = fitz.Matrix(zoom, zoom)
                    pix = page.get_pixmap(matrix=mat)
                    img_data = pix.tobytes("png")
                    img = Image.open(io.BytesIO(img_data))
                    
                    # Configurar OCR optimizado para CVs
                    ocr_config = '--psm 6 --oem 3 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789@.-_()/\\|,;: '
                    
                    ocr_text = pytesseract.image_to_string(
                        img, 
                        lang='spa+eng',
                        config=ocr_config
                    )
                    
                    if ocr_text.strip():
                        text += ocr_text + "\n"
                    else:
                        # Si OCR no funciona, usar el texto disponible
                        text += page_text + "\n"
                        
                except Exception as e:
                    print(f"⚠️ Error en OCR página {page_num}: {e}")
                    text += page_text + "\n"
            else:
                # Si no hay OCR, usar el texto disponible
                text += page_text + "\n"
        
        doc.close()
        return text.strip()
        
    except Exception as e:
        print(f"❌ Error extrayendo texto: {e}")
        return ""

def analyze_cv_with_ai(text: str) -> Dict[str, Any]:
    """
    Analiza el CV usando IA para extraer información de manera inteligente
    """
    if not client:
        return {"error": "Azure OpenAI no configurado"}
    
    try:
        # Prompt optimizado para análisis de CV
        prompt = f"""
Eres un experto en análisis de CVs y recursos humanos. Analiza el siguiente texto extraído de un CV y extrae toda la información relevante de manera estructurada.

TEXTO DEL CV:
{text[:4000]}  # Limitar a 4000 caracteres para evitar tokens excesivos

INSTRUCCIONES:
1. Identifica TODA la información relevante sin importar la estructura del CV
2. Busca información en cualquier formato o disposición
3. Maneja diferentes idiomas (español e inglés)
4. Interpreta fechas en cualquier formato
5. Identifica empresas, cargos, responsabilidades, logros
6. Extrae habilidades técnicas y blandas
7. Detecta formación académica y certificaciones
8. Identifica idiomas y niveles
9. Busca información de contacto

Devuelve SOLO un JSON válido con esta estructura exacta:

{{
  "contacto": {{
    "nombre": "Nombre completo detectado",
    "email": "Email si está presente",
    "telefono": "Teléfono si está presente",
    "ubicacion": "Ubicación si está presente"
  }},
  "experiencia_laboral": [
    {{
      "empresa": "Nombre de la empresa",
      "cargo": "Título del puesto",
      "fecha_inicio": "Fecha de inicio (cualquier formato)",
      "fecha_fin": "Fecha de fin o 'actualidad'",
      "descripcion": "Descripción de responsabilidades y logros",
      "logros": ["Logro 1", "Logro 2"],
      "tecnologias": ["Tecnología 1", "Tecnología 2"]
    }}
  ],
  "formacion_academica": [
    {{
      "titulo": "Título o certificación",
      "institucion": "Institución educativa",
      "fecha_inicio": "Fecha de inicio",
      "fecha_fin": "Fecha de fin o 'actualidad'",
      "nivel": "Grado, Máster, Certificación, etc."
    }}
  ],
  "habilidades_tecnicas": ["Habilidad 1", "Habilidad 2"],
  "habilidades_blandas": ["Habilidad 1", "Habilidad 2"],
  "idiomas": [
    {{
      "idioma": "Nombre del idioma",
      "nivel": "Nivel (Básico, Intermedio, Avanzado, Nativo)"
    }}
  ],
  "certificaciones": ["Certificación 1", "Certificación 2"],
  "proyectos": [
    {{
      "nombre": "Nombre del proyecto",
      "descripcion": "Descripción del proyecto",
      "tecnologias": ["Tecnología 1", "Tecnología 2"],
      "fecha": "Fecha si está disponible"
    }}
  ],
  "resumen_profesional": "Resumen profesional si está presente",
  "intereses": ["Interés 1", "Interés 2"],
  "voluntariado": [
    {{
      "organizacion": "Nombre de la organización",
      "cargo": "Cargo o función",
      "fecha_inicio": "Fecha de inicio",
      "fecha_fin": "Fecha de fin o 'actualidad'",
      "descripcion": "Descripción de las actividades"
    }}
  ]
}}

IMPORTANTE:
- Si no encuentras información para algún campo, usa array vacío [] o string vacío ""
- Interpreta fechas en cualquier formato (2020-2023, Enero 2020, 01/2020, etc.)
- Identifica empresas y cargos aunque no estén claramente separados
- Extrae habilidades técnicas de cualquier contexto (experiencia, proyectos, formación)
- Maneja CVs en español e inglés
- Si hay información ambigua, inclúyela en el campo más apropiado
"""

        response = client.chat.completions.create(
            model=DEPLOYMENT,
            messages=[
                {"role": "system", "content": "Eres un experto en análisis de CVs con más de 10 años de experiencia en recursos humanos. Tu especialidad es extraer información precisa y estructurada de CVs en cualquier formato o idioma."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=4000,
            temperature=0.3,
            response_format={"type": "json_object"}
        )
        
        content = response.choices[0].message.content
        if not content:
            return {"error": "Respuesta vacía de la IA"}
        
        return json.loads(content)
        
    except json.JSONDecodeError as e:
        return {"error": f"Error parseando respuesta JSON: {e}"}
    except Exception as e:
        return {"error": f"Error en análisis con IA: {e}"}

def extract_contact_info_enhanced(text: str) -> Dict[str, str]:
    """
    Extrae información de contacto con patrones mejorados
    """
    contact = {}
    
    # Patrones mejorados para email
    email_patterns = [
        r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        r'\b[A-Za-z0-9._%+-]+\s*@\s*[A-Za-z0-9.-]+\s*\.\s*[A-Z|a-z]{2,}\b'
    ]
    
    for pattern in email_patterns:
        email_match = re.search(pattern, text)
        if email_match:
            contact["email"] = email_match.group().replace(" ", "")
            break
    
    # Patrones mejorados para teléfono
    phone_patterns = [
        r'\+?[\d\s\-\(\)]{9,15}',  # Teléfonos internacionales
        r'[\d\s\-\(\)]{9,}',       # Teléfonos locales
        r'Tel[:\s]*([\d\s\-\(\)]+)',  # Tel: 123-456-789
        r'Phone[:\s]*([\d\s\-\(\)]+)', # Phone: 123-456-789
        r'[Tt]eléfono[:\s]*([\d\s\-\(\)]+)'  # Teléfono: 123-456-789
    ]
    
    for pattern in phone_patterns:
        phone_match = re.search(pattern, text)
        if phone_match:
            phone = phone_match.group(1) if len(phone_match.groups()) > 0 else phone_match.group()
            phone = re.sub(r'[^\d\s\-\(\)\+]', '', phone).strip()
            if len(phone) >= 9 and not re.match(r'\d{4}', phone):
                contact["telefono"] = phone
                break
    
    # Buscar nombre (patrón básico)
    name_patterns = [
        r'^([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)',  # Primera línea con nombre
        r'Nombre[:\s]*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)',
        r'Name[:\s]*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)'
    ]
    
    for pattern in name_patterns:
        name_match = re.search(pattern, text, re.MULTILINE)
        if name_match:
            contact["nombre"] = name_match.group(1)
            break
    
    return contact

def analyze_cv_structure_ai(cv_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analiza la estructura del CV usando los datos extraídos por IA
    """
    # Calcular métricas
    has_contact = bool(cv_data.get("contacto", {}))
    has_experience = len(cv_data.get("experiencia_laboral", [])) > 0
    has_education = len(cv_data.get("formacion_academica", [])) > 0
    has_skills = len(cv_data.get("habilidades_tecnicas", [])) > 0
    has_soft_skills = len(cv_data.get("habilidades_blandas", [])) > 0
    has_languages = len(cv_data.get("idiomas", [])) > 0
    has_projects = len(cv_data.get("proyectos", [])) > 0
    
    # Calcular puntuación de estructura
    structure_score = 0
    if has_contact: structure_score += 1
    if has_experience: structure_score += 3
    if has_education: structure_score += 2
    if has_skills: structure_score += 2
    if has_soft_skills: structure_score += 1
    if has_languages: structure_score += 1
    if has_projects: structure_score += 1
    
    # Evaluar estructura
    if structure_score >= 8:
        structure = "excelente"
    elif structure_score >= 5:
        structure = "bueno"
    elif structure_score >= 3:
        structure = "regular"
    else:
        structure = "mejorable"
    
    # Analizar experiencia
    experience = cv_data.get("experiencia_laboral", [])
    total_years = 0
    
    for exp in experience:
        fecha_inicio = exp.get("fecha_inicio", "")
        fecha_fin = exp.get("fecha_fin", "")
        
        if fecha_inicio and fecha_fin:
            try:
                # Extraer año de inicio
                start_year_match = re.search(r'\d{4}', fecha_inicio)
                if start_year_match:
                    start_year = int(start_year_match.group())
                    
                    # Calcular año de fin
                    if fecha_fin.lower() in ["actualidad", "presente", "hoy", "now"]:
                        end_year = 2024
                    else:
                        end_year_match = re.search(r'\d{4}', fecha_fin)
                        if end_year_match:
                            end_year = int(end_year_match.group())
                        else:
                            end_year = start_year + 1
                    
                    total_years += max(0, end_year - start_year)
            except:
                pass
    
    # Evaluar nivel de experiencia
    if total_years > 5:
        experience_level = "excelente"
    elif total_years > 2:
        experience_level = "bueno"
    elif total_years > 0:
        experience_level = "regular"
    else:
        experience_level = "mejorable"
    
    # Generar fortalezas y debilidades
    strengths = []
    weaknesses = []
    
    if len(cv_data.get("habilidades_tecnicas", [])) > 5:
        strengths.append("Perfil técnico sólido con múltiples tecnologías")
    if len(experience) > 2:
        strengths.append("Experiencia profesional diversa")
    if len(cv_data.get("proyectos", [])) > 0:
        strengths.append("Experiencia en proyectos demostrable")
    if len(cv_data.get("formacion_academica", [])) > 0:
        strengths.append("Formación académica presente")
    if len(cv_data.get("habilidades_blandas", [])) > 3:
        strengths.append("Perfil equilibrado con habilidades blandas")
    if len(cv_data.get("idiomas", [])) > 1:
        strengths.append("Perfil internacional con múltiples idiomas")
    if cv_data.get("resumen_profesional"):
        strengths.append("CV con resumen profesional claro")
    
    if len(cv_data.get("habilidades_tecnicas", [])) < 3:
        weaknesses.append("Pocas habilidades técnicas específicas")
    if len(cv_data.get("habilidades_blandas", [])) < 2:
        weaknesses.append("Falta de habilidades blandas específicas")
    if len(cv_data.get("idiomas", [])) < 2:
        weaknesses.append("Perfil limitado en idiomas")
    if not has_contact:
        weaknesses.append("Información de contacto no detectada")
    if not cv_data.get("resumen_profesional"):
        weaknesses.append("Falta resumen profesional")
    if total_years < 1:
        weaknesses.append("Poca experiencia laboral")
    
    # Generar feedback constructivo
    feedback = ""
    if structure == "excelente":
        feedback += "Tu CV tiene una estructura muy profesional y completa. "
    elif structure == "bueno":
        feedback += "Tu CV tiene una buena estructura, pero podrías mejorarla. "
    else:
        feedback += "Tu CV necesita mejorar su estructura. "
    
    if len(experience) > 0:
        feedback += f"Has incluido {len(experience)} experiencias laborales. "
    
    if len(cv_data.get("habilidades_tecnicas", [])) > 0:
        feedback += f"Has mencionado {len(cv_data.get('habilidades_tecnicas', []))} tecnologías. "
    
    # Alertas
    alerts = []
    if len(cv_data.get("habilidades_tecnicas", [])) < 3:
        alerts.append("Considera agregar más habilidades técnicas específicas")
    if len(cv_data.get("habilidades_blandas", [])) < 2:
        alerts.append("Incluye habilidades blandas como liderazgo, comunicación, trabajo en equipo")
    if len(cv_data.get("idiomas", [])) < 2:
        alerts.append("Considera agregar más idiomas para mejorar tu perfil internacional")
    if not has_contact:
        alerts.append("Asegúrate de incluir información de contacto")
    if not cv_data.get("resumen_profesional"):
        alerts.append("Considera agregar un resumen profesional")
    
    return {
        "structure": structure,
        "coherence": "bueno" if len(experience) > 0 else "mejorable",
        "experience": experience_level,
        "skills": cv_data.get("habilidades_tecnicas", []),
        "softSkills": cv_data.get("habilidades_blandas", []),
        "languages": [f"{lang.get('idioma', '')} ({lang.get('nivel', '')})" for lang in cv_data.get("idiomas", [])],
        "education": [f"{edu.get('titulo', '')} - {edu.get('institucion', '')}" for edu in cv_data.get("formacion_academica", [])],
        "strengths": strengths,
        "weaknesses": weaknesses,
        "feedback": feedback,
        "alerts": alerts,
        "total_years_experience": total_years,
        "technologies_count": len(cv_data.get("habilidades_tecnicas", [])),
        "soft_skills_count": len(cv_data.get("habilidades_blandas", [])),
        "languages_count": len(cv_data.get("idiomas", [])),
        "experience_count": len(experience),
        "education_count": len(cv_data.get("formacion_academica", [])),
        "projects_count": len(cv_data.get("proyectos", []))
    }

def extract_pdf_info(pdf_buffer: bytes) -> Dict[str, Any]:
    """
    Extrae y analiza información de un CV en PDF usando IA avanzada
    """
    try:
        print("🚀 Iniciando análisis avanzado de CV...")
        
        # Extraer texto del PDF con OCR avanzado
        text = extract_text_with_advanced_ocr(pdf_buffer)
        
        if not text.strip():
            return {
                "error": "No se pudo extraer texto del PDF. El archivo puede estar corrupto o ser una imagen sin texto.",
                "cv_info": {},
                "analysis": {},
                "raw_text": ""
            }
        
        print(f"✅ Texto extraído: {len(text)} caracteres")
        
        # Extraer información de contacto mejorada
        contact = extract_contact_info_enhanced(text)
        
        # Analizar CV con IA
        print("🤖 Analizando CV con IA...")
        cv_data = analyze_cv_with_ai(text)
        
        if "error" in cv_data:
            print(f"⚠️ Error en análisis con IA: {cv_data['error']}")
            # Fallback: usar solo información de contacto
            cv_data = {
                "contacto": contact,
                "experiencia_laboral": [],
                "formacion_academica": [],
                "habilidades_tecnicas": [],
                "habilidades_blandas": [],
                "idiomas": [],
                "proyectos": []
            }
        
        # Analizar estructura del CV
        analysis = analyze_cv_structure_ai(cv_data)
        
        # Construir resultado compatible
        cv_info = {
            "contacto": cv_data.get("contacto", {}),
            "software": cv_data.get("habilidades_tecnicas", []),
            "idiomas": [f"{lang.get('idioma', '')} ({lang.get('nivel', '')})" for lang in cv_data.get("idiomas", [])],
            "perfil": cv_data.get("resumen_profesional", ""),
            "experiencia": cv_data.get("experiencia_laboral", []),
            "educacion": cv_data.get("formacion_academica", []),
            "habilidades": cv_data.get("habilidades_blandas", []),
            "proyectos": cv_data.get("proyectos", [])
        }
        
        print("✅ Análisis completado exitosamente")
        
        return {
            "cv_info": cv_info,
            "analysis": analysis,
            "raw_text": text[:1000],  # Primeros 1000 caracteres para debug
            "full_cv_data": cv_data  # Datos completos extraídos por IA
        }
        
    except Exception as e:
        print(f"❌ Error en análisis: {str(e)}")
        return {
            "error": f"Error al procesar el PDF: {str(e)}",
            "cv_info": {},
            "analysis": {},
            "raw_text": ""
        }

if __name__ == "__main__":
    # Para testing directo
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
        with open(pdf_path, 'rb') as f:
            pdf_buffer = f.read()
        result = extract_pdf_info(pdf_buffer)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print("Uso: python cv_analyzer.py <ruta_al_pdf>") 