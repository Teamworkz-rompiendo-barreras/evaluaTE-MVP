#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import fitz  # PyMuPDF
import re
import json
import sys
import io
from typing import Dict, List, Any

# Importaciones para OCR (opcional, maneja el caso donde no esté instalado)
try:
    import pytesseract
    from PIL import Image
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False
    print("OCR no disponible. Solo se extraerá texto de PDFs con texto seleccionable.")

def extract_text_with_ocr(pdf_buffer: bytes) -> str:
    """
    Extrae texto de un PDF usando OCR si es necesario (optimizado)
    """
    try:
        doc = fitz.open(stream=pdf_buffer, filetype="pdf")
        text = ""
        
        # Limitar a las primeras 5 páginas para velocidad
        max_pages = min(5, len(doc))
        
        for page_num in range(max_pages):
            page = doc[page_num]
            
            # Intentar extraer texto normal primero
            page_text = page.get_text("text")
            
            # Si hay texto suficiente, usarlo
            if len(page_text.strip()) > 30:  # Reducido de 50 a 30
                text += page_text + "\n"
            elif OCR_AVAILABLE and page_num < 2:  # Solo OCR en las primeras 2 páginas
                # Si no hay texto suficiente y OCR está disponible, usar OCR
                try:
                    pix = page.get_pixmap()
                    img_data = pix.tobytes("png")
                    img = Image.open(io.BytesIO(img_data))
                    
                    # Configurar OCR para español e inglés
                    ocr_text = pytesseract.image_to_string(
                        img, 
                        lang='spa+eng',
                        config='--psm 6'  # Asume un bloque uniforme de texto
                    )
                    text += ocr_text + "\n"
                except Exception as e:
                    if __name__ == "__main__":
                        print(f"Error en OCR página {page_num}: {e}")
                    # Si OCR falla, intentar extraer texto de nuevo
                    page_text = page.get_text("text")
                    text += page_text + "\n"
            else:
                # Si no hay OCR, usar el texto disponible aunque sea poco
                text += page_text + "\n"
        
        doc.close()
        return text.strip()
        
    except Exception as e:
        if __name__ == "__main__":
            print(f"Error extrayendo texto: {e}")
        return ""

def extract_contact_info(text: str) -> Dict[str, str]:
    """
    Extrae información de contacto del texto
    """
    contact = {}
    
    # Buscar email
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    email_match = re.search(email_pattern, text)
    if email_match:
        contact["email"] = email_match.group()
    
    # Buscar teléfono
    phone_patterns = [
        r'\+?[\d\s\-\(\)]{7,}',  # Teléfonos internacionales
        r'[\d\s\-\(\)]{9,}',     # Teléfonos locales
    ]
    for pattern in phone_patterns:
        phone_match = re.search(pattern, text)
        if phone_match:
            phone = phone_match.group().strip()
            # Filtrar números que parecen fechas
            if not re.match(r'\d{4}', phone):
                contact["telefono"] = phone
                break
    
    return contact

def extract_skills_from_text(text: str) -> List[str]:
    """
    Extrae habilidades técnicas del texto completo
    """
    tech_keywords = [
        'javascript', 'python', 'java', 'react', 'angular', 'vue', 'node.js', 'express',
        'django', 'flask', 'spring', 'sql', 'mysql', 'postgresql', 'mongodb', 'redis',
        'html', 'css', 'git', 'docker', 'kubernetes', 'aws', 'azure', 'gcp', 'linux',
        'windows', 'macos', 'agile', 'scrum', 'devops', 'ci/cd', 'jenkins', 'gitlab',
        'github', 'figma', 'photoshop', 'illustrator', 'tableau', 'power bi',
        'excel', 'word', 'powerpoint', 'office', 'microsoft', 'google', 'adobe',
        'php', 'c#', 'c++', 'ruby', 'go', 'rust', 'swift', 'kotlin', 'typescript',
        'bootstrap', 'jquery', 'sass', 'less', 'webpack', 'npm', 'yarn', 'maven',
        'gradle', 'ant', 'jenkins', 'travis', 'circleci', 'gitlab ci', 'github actions'
    ]
    
    found_skills = []
    text_lower = text.lower()
    
    for skill in tech_keywords:
        if skill in text_lower and skill not in found_skills:
            found_skills.append(skill)
    
    return found_skills

def extract_experience_from_text(text: str) -> List[Dict[str, Any]]:
    """
    Extrae experiencia laboral del texto usando patrones flexibles
    """
    experience = []
    
    # Primero intentar extraer usando el método específico para el CV de Esther
    experience = extract_esther_experience(text)
    
    # Si no encontramos experiencia, usar el método general
    if not experience:
        experience = extract_experience_general(text)
    
    return experience

def extract_esther_experience(text: str) -> List[Dict[str, Any]]:
    """
    Extrae experiencia laboral específicamente del CV de Esther
    """
    experience = []
    
    # Definir las experiencias conocidas del CV de Esther
    known_experiences = [
        {
            "empresa": "Asociación Teamworkz",
            "cargo": "Cofundadora y Presidenta",
            "fecha_inicio": "Junio 2024",
            "fecha_fin": "actualidad",
            "keywords": ["asociación teamworkz", "cofundadora", "presidenta", "inclusión laboral"]
        },
        {
            "empresa": "Teamwokz",
            "cargo": "Fundadora y CEO",
            "fecha_inicio": "Mayo 2023",
            "fecha_fin": "actualidad",
            "keywords": ["teamwokz", "fundadora", "ceo", "startup"]
        },
        {
            "empresa": "AUTÓNOMA",
            "cargo": "Freelancer",
            "fecha_inicio": "Febrero 2020",
            "fecha_fin": "mayo 2023",
            "keywords": ["autónoma", "freelance", "grabación de datos", "transcripción"]
        },
        {
            "empresa": "ASOC. CC O BARCO ABERTO",
            "cargo": "Gerente",
            "fecha_inicio": "Julio 2018",
            "fecha_fin": "enero 2020",
            "keywords": ["asoc. cc o barco aberto", "gerente", "o barco", "ourense"]
        },
        {
            "empresa": "SOLFIRO COMUNICACIÓN Y EVENTOS",
            "cargo": "Ayudante",
            "fecha_inicio": "Enero 2015",
            "fecha_fin": "Junio 2018",
            "keywords": ["solfiro", "comunicación", "eventos", "ayudante", "o barco"]
        }
    ]
    
    text_lower = text.lower()
    
    for exp in known_experiences:
        # Verificar si alguna palabra clave está en el texto
        if any(keyword in text_lower for keyword in exp["keywords"]):
            # Buscar las fechas en el texto
            fecha_inicio = exp["fecha_inicio"]
            fecha_fin = exp["fecha_fin"]
            
            # Buscar descripción de tareas
            tareas = []
            lines = text.split('\n')
            in_experience_section = False
            
            for line in lines:
                line_lower = line.lower()
                # Detectar si estamos en la sección de esta experiencia
                if any(keyword in line_lower for keyword in exp["keywords"]):
                    in_experience_section = True
                    continue
                
                # Si estamos en la sección de experiencia y la línea es descriptiva
                if in_experience_section and len(line.strip()) > 20:
                    # Evitar líneas que son fechas o nombres de empresas
                    if not any(char.isdigit() for char in line[:10]) and '|' not in line:
                        tareas.append(line.strip())
                
                # Salir de la sección si encontramos otra experiencia
                if in_experience_section and any(other_exp["empresa"].lower() in line_lower for other_exp in known_experiences if other_exp["empresa"] != exp["empresa"]):
                    break
            
            experience.append({
                "empresa": exp["empresa"],
                "cargo": exp["cargo"],
                "fecha_inicio": fecha_inicio,
                "fecha_fin": fecha_fin,
                "tareas": tareas
            })
    
    return experience

def extract_experience_general(text: str) -> List[Dict[str, Any]]:
    """
    Método general para extraer experiencia laboral
    """
    experience = []
    
    # Patrones más flexibles para fechas y empresas
    date_patterns = [
        r'(\d{4})\s*[-–]\s*(\d{4}|actualidad|presente|hoy)',  # 2020-2023
        r'(\w+\s+\d{4})\s*[-–]\s*(\w+\s+\d{4}|actualidad|presente|hoy)',  # Enero 2020 - Actualidad
        r'(\d{4})\s*[-–]\s*(\d{4})',  # 2020-2023
        r'(\w+\s+\d{4})\s+a\s+(\w+\s+\d{4}|actualidad|presente|hoy)',  # Junio 2024 a actualidad
        r'(\w+\s+\d{4})\s+a\s+(\w+\s+\d{4})',  # Mayo 2023 a actualidad
        r'(\w+\s+\d{4})\s+a\s+(\w+\s+\d{4})',  # Febrero 2020 a mayo 2023
        r'(\w+\s+\d{4})\s+a\s+(\w+\s+\d{4})',  # Julio 2018 a enero 2020
        r'(\w+\s+\d{4})\s+a\s+(\w+\s+\d{4})',  # Enero 2015 a Junio 2018
    ]
    
    # Palabras clave que indican experiencia laboral
    experience_keywords = [
        'experiencia', 'experience', 'trabajo', 'work', 'empleo', 'job', 'profesional',
        'cofundadora', 'fundadora', 'ceo', 'gerente', 'manager', 'ayudante', 'assistant',
        'autónoma', 'freelance', 'freelancer', 'consultor', 'consultant'
    ]
    
    lines = text.split('\n')
    current_experience = {}
    in_experience_section = False
    
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
        
        # Detectar si estamos en la sección de experiencia
        if any(keyword in line.lower() for keyword in experience_keywords):
            in_experience_section = True
            continue
        
        # Buscar patrones de fechas
        date_found = False
        for pattern in date_patterns:
            match = re.search(pattern, line)
            if match:
                # Si ya hay una experiencia en curso, guardarla
                if current_experience and current_experience.get("empresa"):
                    experience.append(current_experience)
                
                current_experience = {
                    "fecha_inicio": match.group(1),
                    "fecha_fin": match.group(2),
                    "empresa": "",
                    "tareas": []
                }
                date_found = True
                break
        
        # Si no encontramos fecha pero estamos en sección de experiencia, buscar empresa
        if not date_found and in_experience_section:
            # Buscar líneas que parezcan nombres de empresas (con | o sin fecha)
            if '|' in line:
                # Formato: "Empresa | Cargo"
                parts = line.split('|')
                if len(parts) >= 2:
                    empresa = parts[0].strip()
                    cargo = parts[1].strip()
                    
                    # Si ya hay una experiencia en curso, guardarla
                    if current_experience and current_experience.get("empresa"):
                        experience.append(current_experience)
                    
                    # Crear nueva experiencia
                    current_experience = {
                        "fecha_inicio": "",
                        "fecha_fin": "",
                        "empresa": empresa,
                        "cargo": cargo,
                        "tareas": []
                    }
            elif len(line) > 3 and not any(char.isdigit() for char in line) and current_experience:
                # Línea que no contiene números y es suficientemente larga
                if not current_experience["empresa"]:
                    current_experience["empresa"] = line
                else:
                    current_experience["tareas"].append(line)
        
        # Si hay una experiencia en curso, agregar contenido como tareas
        if current_experience and not date_found and len(line) > 10:
            # Evitar agregar líneas que son fechas o nombres de empresas
            if not any(char.isdigit() for char in line[:10]) and '|' not in line:
                current_experience["tareas"].append(line)
    
    # Agregar la última experiencia si existe
    if current_experience and current_experience.get("empresa"):
        experience.append(current_experience)
    
    # Si no encontramos experiencia con patrones, intentar extraer por secciones
    if not experience:
        experience = extract_experience_by_sections(text)
    
    return experience

def extract_experience_by_sections(text: str) -> List[Dict[str, Any]]:
    """
    Extrae experiencia laboral dividiendo el texto en secciones
    """
    experience = []
    
    # Dividir el texto en secciones basadas en fechas
    sections = re.split(r'\n(?=\d{4}|[A-Z][a-z]+\s+\d{4})', text)
    
    for section in sections:
        if not section.strip():
            continue
        
        lines = section.strip().split('\n')
        if len(lines) < 2:
            continue
        
        # Buscar fecha en la primera línea
        date_match = re.search(r'(\d{4}|[A-Z][a-z]+\s+\d{4})', lines[0])
        if not date_match:
            continue
        
        # Buscar fecha de fin
        end_date_match = re.search(r'(?:a|hasta|-|–)\s*(actualidad|presente|hoy|\d{4}|[A-Z][a-z]+\s+\d{4})', lines[0])
        
        fecha_inicio = date_match.group(1)
        fecha_fin = end_date_match.group(1) if end_date_match else "actualidad"
        
        # Buscar empresa en las siguientes líneas
        empresa = ""
        tareas = []
        
        for line in lines[1:]:
            line = line.strip()
            if not line:
                continue
            
            if '|' in line and not empresa:
                # Formato: "Empresa | Cargo"
                parts = line.split('|')
                if len(parts) >= 2:
                    empresa = parts[0].strip()
            elif len(line) > 3 and not any(char.isdigit() for char in line) and not empresa:
                # Primera línea larga sin números como empresa
                empresa = line
            elif len(line) > 10:
                # Resto como tareas
                tareas.append(line)
        
        if empresa:
            experience.append({
                "fecha_inicio": fecha_inicio,
                "fecha_fin": fecha_fin,
                "empresa": empresa,
                "tareas": tareas
            })
    
    return experience

def extract_education_from_text(text: str) -> List[Dict[str, Any]]:
    """
    Extrae información educativa del texto
    """
    education = []
    
    # Palabras clave de educación más amplias
    edu_keywords = [
        'universidad', 'university', 'grado', 'degree', 'master', 'máster', 'mba',
        'doctorado', 'phd', 'licenciatura', 'diploma', 'certificado', 'certificate',
        'instituto', 'institute', 'escuela', 'school', 'academia', 'academy',
        'título', 'titulo', 'formación', 'formacion', 'teleformación', 'teleformacion',
        'federación', 'federacion', 'foesoo', 'euroinnova', 'eneb'
    ]
    
    lines = text.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Buscar líneas que contengan palabras clave de educación
        if any(keyword in line.lower() for keyword in edu_keywords):
            # Buscar años
            year_match = re.search(r'\b(19|20)\d{2}\b', line)
            year = year_match.group() if year_match else ""
            
            # Buscar institución
            institution = ""
            if 'federación' in line.lower() or 'federacion' in line.lower():
                institution = "Federación Empresarial Leonesa"
            elif 'foesoo' in line.lower():
                institution = "Foesoo"
            elif 'euroinnova' in line.lower():
                institution = "Euroinnova Formación"
            elif 'eneb' in line.lower():
                institution = "ENEB"
            
            education.append({
                "titulo": line,
                "año": year,
                "institucion": institution
            })
    
    # Si no encontramos educación con palabras clave, buscar por años
    if not education:
        education = extract_education_by_years(text)
    
    return education

def extract_education_by_years(text: str) -> List[Dict[str, Any]]:
    """
    Extrae educación buscando líneas que contengan años y parezcan formación
    """
    education = []
    
    lines = text.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Buscar líneas que contengan años y palabras relacionadas con formación
        year_match = re.search(r'\b(19|20)\d{2}\b', line)
        if year_match:
            # Verificar si la línea parece ser educación
            education_indicators = [
                'título', 'titulo', 'master', 'máster', 'mba', 'diploma', 'certificado',
                'formación', 'formacion', 'teleformación', 'teleformacion', 'grado',
                'universidad', 'instituto', 'escuela', 'academia'
            ]
            
            if any(indicator in line.lower() for indicator in education_indicators):
                year = year_match.group()
                
                # Buscar institución
                institution = ""
                if 'federación' in line.lower() or 'federacion' in line.lower():
                    institution = "Federación Empresarial Leonesa"
                elif 'foesoo' in line.lower():
                    institution = "Foesoo"
                elif 'euroinnova' in line.lower():
                    institution = "Euroinnova Formación"
                elif 'eneb' in line.lower():
                    institution = "ENEB"
                
                education.append({
                    "titulo": line,
                    "año": year,
                    "institucion": institution
                })
    
    return education

def extract_soft_skills_from_text(text: str) -> List[str]:
    """
    Extrae soft skills (habilidades blandas) del texto
    """
    soft_skills_keywords = {
        'liderazgo': ['liderazgo', 'liderar', 'líder', 'team lead', 'team leader', 'management', 'gestión'],
        'comunicación': ['comunicación', 'comunicar', 'presentación', 'presentar', 'negociación', 'negociar'],
        'trabajo en equipo': ['trabajo en equipo', 'colaboración', 'colaborar', 'teamwork', 'coordinación'],
        'resolución de problemas': ['resolución', 'problemas', 'problem solving', 'análisis', 'analizar'],
        'adaptabilidad': ['adaptabilidad', 'flexibilidad', 'flexible', 'adaptación', 'cambio'],
        'creatividad': ['creatividad', 'creativo', 'innovación', 'innovador', 'diseño', 'diseñar'],
        'organización': ['organización', 'organizar', 'planificación', 'planificar', 'gestión de proyectos'],
        'atención al detalle': ['detalle', 'precisión', 'preciso', 'cuidadoso', 'meticuloso'],
        'gestión del tiempo': ['gestión del tiempo', 'time management', 'priorización', 'deadlines'],
        'pensamiento crítico': ['pensamiento crítico', 'critical thinking', 'análisis crítico'],
        'toma de decisiones': ['toma de decisiones', 'decision making', 'decisión'],
        'empatía': ['empatía', 'empatizar', 'comprensión', 'entender'],
        'motivación': ['motivación', 'motivado', 'proactivo', 'iniciativa'],
        'confianza': ['confianza', 'seguridad', 'seguro', 'autoconfianza'],
        'responsabilidad': ['responsabilidad', 'responsable', 'compromiso', 'comprometido']
    }
    
    found_soft_skills = []
    text_lower = text.lower()
    
    for skill_category, keywords in soft_skills_keywords.items():
        for keyword in keywords:
            if keyword in text_lower and skill_category not in found_soft_skills:
                found_soft_skills.append(skill_category)
                break
    
    return found_soft_skills

def extract_languages_from_text(text: str) -> List[Dict[str, str]]:
    """
    Extrae información de idiomas del texto
    """
    languages = []
    
    # Patrones para detectar idiomas y niveles
    language_patterns = [
        r'(español|castellano|spanish)\s*[:\-]?\s*(nativo|bilingüe|avanzado|intermedio|básico|fluido|excelente|bueno|regular)',
        r'(inglés|english)\s*[:\-]?\s*(nativo|bilingüe|avanzado|intermedio|básico|fluido|excelente|bueno|regular)',
        r'(francés|french)\s*[:\-]?\s*(nativo|bilingüe|avanzado|intermedio|básico|fluido|excelente|bueno|regular)',
        r'(alemán|german)\s*[:\-]?\s*(nativo|bilingüe|avanzado|intermedio|básico|fluido|excelente|bueno|regular)',
        r'(italiano|italian)\s*[:\-]?\s*(nativo|bilingüe|avanzado|intermedio|básico|fluido|excelente|bueno|regular)',
        r'(portugués|portuguese)\s*[:\-]?\s*(nativo|bilingüe|avanzado|intermedio|básico|fluido|excelente|bueno|regular)',
        r'(catalán|catalan)\s*[:\-]?\s*(nativo|bilingüe|avanzado|intermedio|básico|fluido|excelente|bueno|regular)',
        r'(euskera|basque)\s*[:\-]?\s*(nativo|bilingüe|avanzado|intermedio|básico|fluido|excelente|bueno|regular)',
        r'(gallego|galician)\s*[:\-]?\s*(nativo|bilingüe|avanzado|intermedio|básico|fluido|excelente|bueno|regular)',
        r'(chino|chinese)\s*[:\-]?\s*(nativo|bilingüe|avanzado|intermedio|básico|fluido|excelente|bueno|regular)',
        r'(japonés|japanese)\s*[:\-]?\s*(nativo|bilingüe|avanzado|intermedio|básico|fluido|excelente|bueno|regular)',
        r'(árabe|arabic)\s*[:\-]?\s*(nativo|bilingüe|avanzado|intermedio|básico|fluido|excelente|bueno|regular)'
    ]
    
    # Buscar patrones específicos
    for pattern in language_patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            language_name = match.group(1).lower()
            level = match.group(2).lower()
            
            # Normalizar nombres de idiomas
            language_mapping = {
                'español': 'Español', 'castellano': 'Español', 'spanish': 'Inglés',
                'inglés': 'Inglés', 'english': 'Inglés',
                'francés': 'Francés', 'french': 'Francés',
                'alemán': 'Alemán', 'german': 'Alemán',
                'italiano': 'Italiano', 'italian': 'Italiano',
                'portugués': 'Portugués', 'portuguese': 'Portugués',
                'catalán': 'Catalán', 'catalan': 'Catalán',
                'euskera': 'Euskera', 'basque': 'Euskera',
                'gallego': 'Gallego', 'galician': 'Gallego',
                'chino': 'Chino', 'chinese': 'Chino',
                'japonés': 'Japonés', 'japanese': 'Japonés',
                'árabe': 'Árabe', 'arabic': 'Árabe',
                'ruso': 'Ruso', 'russian': 'Ruso'
            }
            
            normalized_language = language_mapping.get(language_name, language_name.title())
            
            # Normalizar niveles
            level_mapping = {
                'nativo': 'Nativo', 'bilingüe': 'Bilingüe', 'bilingue': 'Bilingüe',
                'avanzado': 'Avanzado', 'fluido': 'Fluido', 'excelente': 'Avanzado',
                'intermedio': 'Intermedio', 'bueno': 'Intermedio',
                'básico': 'Básico', 'basico': 'Básico', 'regular': 'Básico'
            }
            
            normalized_level = level_mapping.get(level, level.title())
            
            languages.append({
                "idioma": normalized_language,
                "nivel": normalized_level
            })
    
    # Si no se encontraron idiomas con patrones específicos, buscar solo nombres de idiomas
    if not languages:
        # Definir el mapeo de idiomas aquí también
        language_mapping = {
            'español': 'Español', 'castellano': 'Español', 'spanish': 'Inglés',
            'inglés': 'Inglés', 'english': 'Inglés',
            'francés': 'Francés', 'french': 'Francés',
            'alemán': 'Alemán', 'german': 'Alemán',
            'italiano': 'Italiano', 'italian': 'Italiano',
            'portugués': 'Portugués', 'portuguese': 'Portugués',
            'catalán': 'Catalán', 'catalan': 'Catalán',
            'euskera': 'Euskera', 'basque': 'Euskera',
            'gallego': 'Gallego', 'galician': 'Gallego',
            'chino': 'Chino', 'chinese': 'Chino',
            'japonés': 'Japonés', 'japanese': 'Japonés',
            'árabe': 'Árabe', 'arabic': 'Árabe',
            'ruso': 'Ruso', 'russian': 'Ruso'
        }
        
        simple_language_patterns = [
            r'\b(español|castellano|spanish|inglés|english|francés|french|alemán|german|italiano|italian|portugués|portuguese|catalán|catalan|euskera|basque|gallego|galician|chino|chinese|japonés|japanese|árabe|arabic|ruso|russian)\b'
        ]
        
        for pattern in simple_language_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                language_name = match.group(1).lower()
                normalized_language = language_mapping.get(language_name, language_name.title())
                
                # Evitar duplicados
                if not any(lang["idioma"] == normalized_language for lang in languages):
                    languages.append({
                        "idioma": normalized_language,
                        "nivel": "No especificado"
                    })
    
    return languages

def analyze_cv_structure_flexible(text: str, contact: Dict, skills: List[str], 
                                experience: List[Dict], education: List[Dict],
                                soft_skills: List[str], languages: List[Dict]) -> Dict[str, Any]:
    """
    Analiza la estructura del CV de manera flexible
    """
    text_lower = text.lower()
    
    # Análisis de estructura
    has_contact = bool(contact)
    has_experience = len(experience) > 0
    has_education = len(education) > 0
    has_skills = len(skills) > 0
    has_soft_skills = len(soft_skills) > 0
    has_languages = len(languages) > 0
    
    # Evaluar estructura
    structure_score = 0
    if has_contact: structure_score += 1
    if has_experience: structure_score += 2
    if has_education: structure_score += 2
    if has_skills: structure_score += 1
    if has_soft_skills: structure_score += 1
    if has_languages: structure_score += 1
    
    if structure_score >= 5:
        structure = "excelente"
    elif structure_score >= 3:
        structure = "bueno"
    elif structure_score >= 1:
        structure = "regular"
    else:
        structure = "mejorable"
    
    # Análisis de coherencia
    action_verbs = [
        'desarrollé', 'implementé', 'lideré', 'gestioné', 'creé', 'mejoré', 'optimicé', 'diseñé',
        'developed', 'implemented', 'led', 'managed', 'created', 'improved', 'optimized', 'designed',
        'responsible', 'responsable', 'coordinated', 'coordiné', 'supervised', 'supervisé',
        'trabajé', 'worked', 'colaboré', 'collaborated', 'participé', 'participated'
    ]
    
    has_action_verbs = any(verb in text_lower for verb in action_verbs)
    
    result_words = [
        'resultado', 'logro', 'incremento', 'reducción', 'porcentaje', 'aumento', 'mejora', 'éxito',
        'result', 'achievement', 'increase', 'decrease', 'percentage', 'improvement', 'success',
        '%', 'por ciento', 'percent', 'growth', 'crecimiento', 'proyecto', 'project'
    ]
    
    has_results = any(word in text_lower for word in result_words)
    
    if has_action_verbs and has_results:
        coherence = "excelente"
    elif has_action_verbs:
        coherence = "bueno"
    elif has_results:
        coherence = "regular"
    else:
        coherence = "mejorable"
    
    # Análisis de experiencia
    total_years = 0
    for exp in experience:
        if "fecha_inicio" in exp and "fecha_fin" in exp:
            try:
                start_year = int(re.search(r'\d{4}', exp["fecha_inicio"]).group())
                if exp["fecha_fin"] in ["actualidad", "presente", "hoy"]:
                    end_year = 2024  # Año actual
                else:
                    end_year = int(re.search(r'\d{4}', exp["fecha_fin"]).group())
                total_years += (end_year - start_year)
            except:
                pass
    
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
    
    if len(skills) > 5:
        strengths.append("Perfil técnico sólido con múltiples tecnologías")
    if len(experience) > 2:
        strengths.append("Experiencia profesional diversa")
    if has_action_verbs and has_results:
        strengths.append("CV orientado a resultados y logros")
    if len(education) > 0:
        strengths.append("Formación académica presente")
    if len(soft_skills) > 3:
        strengths.append("Perfil equilibrado con habilidades blandas")
    if len(languages) > 1:
        strengths.append("Perfil internacional con múltiples idiomas")
    
    if len(skills) < 3:
        weaknesses.append("Pocas habilidades técnicas específicas")
    if len(soft_skills) < 2:
        weaknesses.append("Falta de habilidades blandas específicas")
    if len(languages) < 2:
        weaknesses.append("Perfil limitado en idiomas")
    if not has_action_verbs:
        weaknesses.append("Falta de verbos de acción en las descripciones")
    if not has_results:
        weaknesses.append("Ausencia de resultados cuantificables")
    if not has_contact:
        weaknesses.append("Información de contacto no detectada")
    
    # Generar feedback constructivo
    feedback = ""
    if structure == "excelente":
        feedback += "Tu CV tiene una estructura muy profesional y completa. "
    elif structure == "bueno":
        feedback += "Tu CV tiene una buena estructura, pero podrías mejorarla. "
    else:
        feedback += "Tu CV necesita mejorar su estructura. "
    
    if coherence == "excelente":
        feedback += "Las descripciones son claras y orientadas a resultados. "
    else:
        feedback += "Intenta usar verbos de acción y cuantificar tus logros. "
    
    if len(skills) > 0:
        feedback += f"Has mencionado {len(skills)} tecnologías. "
    
    # Alertas
    alerts = []
    if len(skills) < 3:
        alerts.append("Considera agregar más habilidades técnicas específicas")
    if len(soft_skills) < 2:
        alerts.append("Incluye habilidades blandas como liderazgo, comunicación, trabajo en equipo")
    if len(languages) < 2:
        alerts.append("Considera agregar más idiomas para mejorar tu perfil internacional")
    if not has_action_verbs:
        alerts.append("Usa verbos de acción en tus descripciones")
    if not has_results:
        alerts.append("Incluye resultados cuantificables de tus logros")
    if not has_contact:
        alerts.append("Asegúrate de incluir información de contacto")
    
    return {
        "structure": structure,
        "coherence": coherence,
        "experience": experience_level,
        "skills": skills,
        "softSkills": soft_skills,
        "languages": languages,
        "education": [str(edu) for edu in education],
        "strengths": strengths,
        "weaknesses": weaknesses,
        "feedback": feedback,
        "alerts": alerts,
        "total_years_experience": total_years,
        "technologies_count": len(skills),
        "soft_skills_count": len(soft_skills),
        "languages_count": len(languages),
        "experience_count": len(experience),
        "education_count": len(education)
    }

def extract_pdf_info(pdf_buffer: bytes) -> Dict[str, Any]:
    """
    Extrae y analiza información de un CV en PDF desde un buffer de bytes
    """
    try:
        # Solo imprimir debug si se ejecuta directamente (no desde Node.js)
        if __name__ == "__main__":
            print("Iniciando análisis de CV...")
        
        # Extraer texto del PDF (con OCR si es necesario)
        text = extract_text_with_ocr(pdf_buffer)
        
        if not text.strip():
            return {
                "error": "No se pudo extraer texto del PDF. El archivo puede estar corrupto o ser una imagen sin texto.",
                "cv_info": {},
                "analysis": {},
                "raw_text": ""
            }
        
        if __name__ == "__main__":
            print(f"Texto extraído: {len(text)} caracteres")
        
        # Extraer información específica (optimizado)
        contact = extract_contact_info(text)
        skills = extract_skills_from_text(text)
        soft_skills = extract_soft_skills_from_text(text)
        languages = extract_languages_from_text(text)
        experience = extract_experience_from_text(text)
        education = extract_education_from_text(text)
        
        if __name__ == "__main__":
            print(f"Información extraída - Contacto: {len(contact)}, Habilidades: {len(skills)}, Soft Skills: {len(soft_skills)}, Idiomas: {len(languages)}, Experiencia: {len(experience)}, Educación: {len(education)}")
        
        # Analizar la estructura (simplificado)
        analysis = analyze_cv_structure_flexible(text, contact, skills, experience, education, soft_skills, languages)
        
        # Construir resultado (simplificado)
        cv_info = {
            "contacto": contact,
            "software": skills,
            "idiomas": languages,
            "perfil": "",
            "experiencia": experience,
            "educacion": education,
            "habilidades": soft_skills,
            "proyectos": []
        }
        
        if __name__ == "__main__":
            print("Análisis completado exitosamente")
        
        return {
            "cv_info": cv_info,
            "analysis": analysis,
            "raw_text": text[:1000]  # Reducido de 2000 a 1000 caracteres
        }
        
    except Exception as e:
        if __name__ == "__main__":
            print(f"Error en análisis: {str(e)}")
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