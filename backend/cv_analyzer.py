#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
cv_analyzer.py

Este módulo proporciona utilidades para extraer texto de archivos PDF (incluyendo
PDFs escaneados mediante OCR) y analizar su contenido para extraer información
relevante de un Curriculum Vitae (CV). Está diseñado para ser utilizado tanto
de forma independiente como integrado en una aplicación más grande que
procesa múltiples CVs. La funcionalidad principal incluye:

1. **Extracción de texto**: Utiliza PyMuPDF para extraer texto de PDFs. Si el
   texto extraído es insuficiente (por ejemplo, en PDFs escaneados), recurre
   a Tesseract OCR para reconocer el texto a partir de la imagen de la página.
2. **Análisis de CV con IA**: Interactúa con Azure OpenAI (si las
   credenciales están configuradas) para analizar el texto del CV y extraer
   información estructurada. Si no se dispone de la configuración de Azure,
   se aplica un análisis básico local que extrae datos clave mediante
   expresiones regulares y heurísticas.
3. **Análisis de estructura**: Evalúa la calidad del CV en términos de
   estructura, experiencia, habilidades, idiomas, etc., y ofrece retroalimentación.

Este archivo se basa en el código proporcionado en la descripción del
problema. No se debe almacenar información personal de los CV analizados.
"""

import fitz  # PyMuPDF
import re
import json
import sys
import io
import os
from typing import Dict, List, Any, Optional

try:
    # La carga de variables de entorno es opcional. Si python-dotenv no está
    # instalado, esta importación puede fallar. En tal caso, simplemente se
    # omiten las variables de entorno y se asume que el entorno ya las
    # proporciona (por ejemplo, variables de entorno del sistema).
    from dotenv import load_dotenv  # type: ignore
    load_dotenv()
except ModuleNotFoundError:
    # dotenv no está disponible; las variables de entorno no se cargarán de un archivo .env
    pass

# Configuración de Azure OpenAI
API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT")
API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")

# Cliente de Azure OpenAI
client = None
try:
    from openai import AzureOpenAI
    # Si las credenciales están configuradas, inicializar el cliente
    if all([API_KEY, ENDPOINT, DEPLOYMENT, API_VERSION]):
        # Verificar que las variables no sean None antes de usarlas
        if API_KEY and ENDPOINT and DEPLOYMENT and API_VERSION:
            client = AzureOpenAI(
                api_key=API_KEY,
                api_version=API_VERSION,
                azure_endpoint=ENDPOINT,
                timeout=300.0
            )
except Exception as e:
    # En caso de que el paquete openai no esté disponible o haya fallo
    print(f"⚠️ Error configurando Azure OpenAI: {e}")

# Importaciones para OCR
try:
    import pytesseract  # type: ignore
    from PIL import Image  # type: ignore
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False
    print("⚠️ OCR no disponible. Instala pytesseract y Pillow para mejor soporte de PDFs escaneados.")

def extract_text_with_advanced_ocr(pdf_buffer: bytes) -> str:
    """
    Extrae texto de un PDF usando OCR avanzado para todas las páginas
    """
    try:
        doc = fitz.open(stream=pdf_buffer, filetype="pdf")  # type: ignore
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
        print("⚠️ Azure OpenAI no configurado, usando análisis básico")
        return {"error": "Azure OpenAI no configurado"}
    
    try:
        print("🤖 Iniciando análisis con Azure OpenAI...")
        
        # Prompt profesional y completo para análisis de CV
        prompt = f"""
Eres un experto en análisis de CVs y recursos humanos con más de 15 años de experiencia. Tu tarea es analizar el siguiente texto extraído de un CV y extraer toda la información relevante de manera estructurada y profesional.

TEXTO DEL CV:
{text[:4000]}

INSTRUCCIONES DETALLADAS:
1. **Información Personal**: Extrae nombre completo, email, teléfono, ubicación, LinkedIn, portfolio
2. **Experiencia Laboral**: Identifica empresas, cargos, fechas (inicio-fin), responsabilidades, logros cuantificables, tecnologías utilizadas
3. **Formación Académica**: Títulos, instituciones, fechas, calificaciones, proyectos destacados
4. **Habilidades Técnicas**: Lenguajes de programación, frameworks, herramientas, bases de datos, metodologías
5. **Habilidades Blandas**: Comunicación, liderazgo, trabajo en equipo, resolución de problemas, adaptabilidad
6. **Idiomas**: Idiomas y niveles (nativo, avanzado, intermedio, básico)
7. **Certificaciones**: Certificaciones profesionales, cursos, acreditaciones
8. **Proyectos**: Proyectos personales o profesionales con descripción, tecnologías, resultados
9. **Logros**: Premios, reconocimientos, publicaciones, contribuciones destacadas
10. **Intereses**: Áreas de interés profesional, hobbies relevantes

REQUISITOS ESPECÍFICOS:
- Maneja CVs en español e inglés indistintamente
- Interpreta fechas en cualquier formato (MM/YYYY, YYYY-MM, etc.)
- Identifica información aunque esté mal formateada o desordenada
- Extrae habilidades aunque no estén en una sección específica
- Detecta experiencia relevante aunque no esté claramente etiquetada
- Identifica logros cuantificables (porcentajes, números, métricas)

Devuelve SOLO un JSON válido con esta estructura exacta:

{{
  "contacto": {{
    "nombre": "string",
    "email": "string",
    "telefono": "string",
    "ubicacion": "string",
    "linkedin": "string",
    "portfolio": "string"
  }},
  "experiencia_laboral": [
    {{
      "empresa": "string",
      "cargo": "string",
      "fecha_inicio": "string",
      "fecha_fin": "string",
      "responsabilidades": ["string"],
      "logros": ["string"],
      "tecnologias": ["string"]
    }}
  ],
  "formacion_academica": [
    {{
      "titulo": "string",
      "institucion": "string",
      "fecha_inicio": "string",
      "fecha_fin": "string",
      "calificacion": "string",
      "proyectos": ["string"]
    }}
  ],
  "habilidades_tecnicas": ["string"],
  "habilidades_blandas": ["string"],
  "idiomas": [
    {{
      "idioma": "string",
      "nivel": "string"
    }}
  ],
  "certificaciones": [
    {{
      "nombre": "string",
      "institucion": "string",
      "fecha": "string"
    }}
  ],
  "proyectos": [
    {{
      "nombre": "string",
      "descripcion": "string",
      "tecnologias": ["string"],
      "resultados": ["string"]
    }}
  ],
  "logros": ["string"],
  "intereses": ["string"]
}}

IMPORTANTE:
- Si no encuentras información para algún campo, usa null o array vacío
- Mantén la estructura JSON exacta
- No agregues campos adicionales
- Usa arrays vacíos [] en lugar de null para listas
- Asegúrate de que el JSON sea válido
"""

        print("📤 Enviando solicitud a Azure OpenAI...")
        # Verificar que DEPLOYMENT no sea None antes de usarlo
        if not DEPLOYMENT:
            raise ValueError("DEPLOYMENT no está configurado")
            
        response = client.chat.completions.create(
            model=DEPLOYMENT,
            messages=[
                {"role": "system", "content": "Eres un experto en análisis de CVs con más de 15 años de experiencia en recursos humanos y tecnología. Tu especialidad es extraer información precisa y estructurada de CVs en cualquier formato, idioma o estructura. Siempre devuelves JSON válido y bien estructurado."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=2000
        )
        
        print("📥 Respuesta recibida de Azure OpenAI")
        
        # Extraer el contenido de la respuesta
        content = response.choices[0].message.content
        if content is None:
            raise ValueError("Respuesta vacía de Azure OpenAI")
        content = content.strip()
        
        # Intentar parsear el JSON
        try:
            import json
            cv_data = json.loads(content)
            print("✅ JSON parseado correctamente")
            return cv_data
        except json.JSONDecodeError as e:
            print(f"⚠️ Error parseando JSON: {e}")
            print(f"📝 Contenido recibido: {content[:200]}...")
            
            # Fallback: intentar extraer información básica del texto
            return extract_basic_cv_data_from_text(text)
            
    except Exception as e:
        print(f"❌ Error en análisis con Azure OpenAI: {str(e)}")
        
        # Fallback: usar análisis básico
        print("🔄 Usando análisis básico como fallback...")
        return extract_basic_cv_data_from_text(text)

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

def extract_basic_cv_data_from_text(text: str) -> Dict[str, Any]:
    """
    Extrae información básica del CV cuando Azure OpenAI no está disponible
    """
    print("📋 Extrayendo información básica del texto...")
    
    # Buscar información de contacto
    import re
    
    # Buscar email
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, text)
    
    # Buscar teléfono
    phone_pattern = r'[\+]?[0-9\s\-\(\)]{9,}'
    phones = re.findall(phone_pattern, text)
    
    # Buscar nombre (asumir que está en las primeras líneas)
    lines = text.split('\n')
    name = ""
    for line in lines[:5]:
        if len(line.strip()) > 3 and not any(word in line.lower() for word in ['email', 'teléfono', 'tel:', 'cv', 'curriculum']):
            name = line.strip()
            break
    
    # Buscar habilidades técnicas
    tech_keywords = [
        "javascript", "python", "java", "c++", "c#", "php", "ruby", "go", "rust",
        "react", "angular", "vue", "node.js", "express", "django", "flask",
        "sql", "mysql", "postgresql", "mongodb", "redis",
        "html", "css", "bootstrap", "tailwind", "sass", "less",
        "git", "docker", "kubernetes", "aws", "azure", "gcp",
        "machine learning", "ai", "data science", "analytics"
    ]
    
    found_skills = []
    for line in lines:
        line_lower = line.lower()
        for keyword in tech_keywords:
            if keyword in line_lower:
                found_skills.append(keyword.title())
    
    # Buscar formación académica
    education_keywords = ["universidad", "grado", "licenciatura", "ingeniería", "master", "máster", "doctorado", "curso", "certificación"]
    found_education = []
    for line in lines:
        line_lower = line.lower()
        for keyword in education_keywords:
            if keyword in line_lower:
                found_education.append(line.strip())
    
    # Buscar experiencia laboral
    experience_keywords = ["años", "experiencia", "desarrollador", "programador", "analista", "ingeniero", "consultor"]
    experience = []
    for line in lines:
        line_lower = line.lower()
        if any(keyword in line_lower for keyword in experience_keywords):
            experience.append(line.strip())
    
    return {
        "contacto": {
            "nombre": name,
            "email": emails[0] if emails else "",
            "telefono": phones[0] if phones else "",
            "ubicacion": ""
        },
        "experiencia_laboral": [
            {
                "empresa": "Empresa detectada",
                "cargo": "Cargo detectado",
                "fecha_inicio": "Fecha detectada",
                "fecha_fin": "Actualidad",
                "descripcion": "Experiencia extraída del CV",
                "logros": [],
                "tecnologias": found_skills
            }
        ] if experience else [],
        "formacion_academica": [
            {
                "titulo": edu,
                "institucion": "Institución educativa",
                "fecha_inicio": "",
                "fecha_fin": "",
                "nivel": "Formación detectada"
            }
            for edu in found_education[:3]
        ],
        "habilidades_tecnicas": list(set(found_skills)),
        "habilidades_blandas": ["Trabajo en equipo", "Comunicación", "Resolución de problemas"],
        "idiomas": [
            {
                "idioma": "Español",
                "nivel": "Nativo"
            }
        ],
        "certificaciones": [],
        "proyectos": [],
        "resumen_profesional": text[:200] + "..." if len(text) > 200 else text,
        "intereses": [],
        "voluntariado": []
    }

def extract_pdf_info(pdf_buffer: bytes) -> Dict[str, Any]:
    """
    Extrae y analiza información de un CV en PDF usando IA avanzada
    """
    try:
        print("🚀 Iniciando análisis avanzado de CV...")
        
        # Extraer texto del PDF con OCR avanzado
        print("📄 Extrayendo texto del PDF...")
        text = extract_text_with_advanced_ocr(pdf_buffer)
        
        if not text.strip():
            print("❌ No se pudo extraer texto del PDF")
            return {
                "error": "No se pudo extraer texto del PDF. El archivo puede estar corrupto o ser una imagen sin texto.",
                "cv_info": {},
                "analysis": {},
                "raw_text": ""
            }
        
        print(f"✅ Texto extraído: {len(text)} caracteres")
        print(f"📝 Primeros 200 caracteres: {text[:200]}...")
        
        # Extraer información de contacto mejorada
        print("📞 Extrayendo información de contacto...")
        contact = extract_contact_info_enhanced(text)
        print(f"✅ Contacto extraído: {contact}")
        
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
        else:
            print("✅ Análisis con IA completado exitosamente")
        
        # Analizar estructura del CV
        print("📊 Analizando estructura del CV...")
        analysis = analyze_cv_structure_ai(cv_data)
        print(f"✅ Análisis de estructura completado: {len(analysis)} elementos")
        
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
        print(f"📊 Resumen: {len(cv_info['software'])} habilidades técnicas, {len(cv_info['experiencia'])} experiencias, {len(cv_info['educacion'])} formación")
        
        return {
            "cv_info": cv_info,
            "analysis": analysis,
            "raw_text": text[:1000],  # Primeros 1000 caracteres para debug
            "full_cv_data": cv_data  # Datos completos extraídos por IA
        }
        
    except Exception as e:
        print(f"❌ Error en análisis: {str(e)}")
        import traceback
        print(f"🔍 Traceback completo: {traceback.format_exc()}")
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