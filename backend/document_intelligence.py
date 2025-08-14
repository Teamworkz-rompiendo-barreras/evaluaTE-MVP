#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
document_intelligence_improved.py

Versión mejorada del análisis de CVs con parsing más robusto y detección de patrones avanzada.
"""

import os
import json
import logging
import re
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from typing import Tuple
from datetime import datetime
import tempfile
from dotenv import load_dotenv

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cargar variables de entorno
load_dotenv()

try:
    from azure.ai.formrecognizer import DocumentAnalysisClient
    from azure.core.credentials import AzureKeyCredential
    from azure.storage.blob import BlobServiceClient
    DOCUMENT_INTELLIGENCE_AVAILABLE = True
except ImportError:
    DOCUMENT_INTELLIGENCE_AVAILABLE = False
    logger.warning("Azure AI Document Intelligence no disponible")

# Dependencias opcionales para normalización robusta
try:  # type: ignore
    import dateparser  # type: ignore
except Exception:  # pragma: no cover
    dateparser = None  # type: ignore

try:  # type: ignore
    import phonenumbers  # type: ignore
except Exception:  # pragma: no cover
    phonenumbers = None  # type: ignore

# Catálogo simple de títulos de sección y meses para heurísticas
SECTION_TITLES = {
    "experiencia": ["experiencia", "laboral", "work experience", "employment", "trayectoria", "historial"],
    "educacion": ["educación", "formación", "estudios", "education", "academic"],
    "idiomas": ["idiomas", "languages", "lenguas"],
    "habilidades": ["habilidades", "skills", "competencias", "tecnologías", "tools", "technologies"],
    "proyectos": ["proyectos", "projects", "portfolio"],
    "resumen": ["perfil", "resumen", "summary", "sobre mí", "about me", "objetivo", "objetivos"],
}

MONTHS_RE = (
    r"(ene|feb|mar|abr|may|jun|jul|ago|sep|oct|nov|dic|"
    r"enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|setiembre|octubre|noviembre|diciembre|"
    r"jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)"
)

DATE_RANGE_RE = re.compile(
    rf"(?P<start>(?:{MONTHS_RE}\.?(?:\s+\d{{4}})?)|\d{{1,2}}[/-]\d{{1,2}}[/-]\d{{2,4}}|\d{{4}})\s*[-–—a]\s*"
    rf"(?P<end>(?:{MONTHS_RE}\.?(?:\s+\d{{4}})?)|\d{{1,2}}[/-]\d{{1,2}}[/-]\d{{2,4}}|actualidad|presente|now|current)",
    re.IGNORECASE,
)

@dataclass
class Block:
    text: str
    page: int
    bbox: Tuple[float, float, float, float]  # xmin, ymin, xmax, ymax
    col: int = 0
    is_heading: bool = False
    heading_key: Optional[str] = None

class ImprovedDocumentIntelligenceService:
    """
    Servicio mejorado para análisis de documentos con parsing robusto
    """
    
    def __init__(self):
        self.endpoint = os.getenv('AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT')
        self.key = os.getenv('AZURE_DOCUMENT_INTELLIGENCE_KEY')
        self.model_id = os.getenv('AZURE_DOCINTEL_MODEL_ID')  # opcional: modelo custom
        self.storage_connection_string = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
        self.container_name = os.getenv('AZURE_STORAGE_CONTAINER', 'cv-uploads')
        
        self.client = None
        self.blob_service_client = None
        
        if DOCUMENT_INTELLIGENCE_AVAILABLE and self.endpoint and self.key:
            try:
                self.client = DocumentAnalysisClient(
                    endpoint=self.endpoint, 
                    credential=AzureKeyCredential(self.key)
                )
                logger.info("✅ Azure AI Document Intelligence configurado correctamente")
            except Exception as e:
                logger.error(f"❌ Error configurando Document Intelligence: {e}")
                self.client = None
    
    def is_configured(self) -> bool:
        """Verifica si el servicio está configurado correctamente"""
        return self.client is not None
    
    def _validate_document_intelligence_response(self, result) -> bool:
        """Valida que la respuesta de Document Intelligence sea correcta"""
        try:
            # Verificar que el resultado existe
            if not result:
                logger.error("❌ Resultado de Document Intelligence es None")
                return False
            
            # Verificar que tiene el atributo content
            if not hasattr(result, 'content'):
                logger.error("❌ Resultado no tiene atributo 'content'")
                return False
            
            # Verificar que el contenido no esté vacío
            if not result.content or not result.content.strip():
                logger.error("❌ Contenido de Document Intelligence está vacío")
                return False
            
            # Verificar que tiene páginas (opcional)
            if hasattr(result, 'pages') and not result.pages:
                logger.warning("⚠️ Document Intelligence no detectó páginas")
            
            logger.info("✅ Respuesta de Document Intelligence válida")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error validando respuesta de Document Intelligence: {e}")
            return False

    def analyze_cv_with_improved_intelligence(self, pdf_buffer: bytes) -> Dict[str, Any]:
        """
        Analiza un CV usando Azure AI Document Intelligence con parsing mejorado
        """
        if not self.is_configured():
            return {
                "error": "Azure AI Document Intelligence no está configurado",
                "cv_info": {},
                "analysis": {},
                "raw_text": ""
            }
        
        try:
            logger.info("🚀 Iniciando análisis mejorado con Azure AI Document Intelligence...")
            
            # Crear archivo temporal para el análisis
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
                temp_file.write(pdf_buffer)
                temp_file_path = temp_file.name
            
            try:
                # Analizar documento
                with open(temp_file_path, "rb") as document:
                    # Elegir modelo: custom si está definido, sino prebuilt-layout
                    model_to_use = (self.model_id or "prebuilt-layout").strip()
                    logger.info(f"📄 Iniciando análisis con Azure AI Document Intelligence (modelo='{model_to_use}')...")
                    try:
                        poller = self.client.begin_analyze_document(model_to_use, document)
                        result = poller.result()
                    except Exception as e:
                        if model_to_use != "prebuilt-layout":
                            logger.warning(f"⚠️ Falló el modelo custom '{model_to_use}', reintentando con 'prebuilt-layout': {e}")
                            document.seek(0)
                            poller = self.client.begin_analyze_document("prebuilt-layout", document)
                            result = poller.result()
                        else:
                            raise
                    logger.info("✅ Análisis de Document Intelligence completado")
                
                # Validar la respuesta de Document Intelligence
                if not self._validate_document_intelligence_response(result):
                    raise ValueError("Respuesta inválida de Document Intelligence")
                
                logger.info(f"📝 Texto extraído: {len(result.content)} caracteres")
                
                # Extraer datos estructurados mejorados
                cv_data = self._extract_improved_structured_data(result)
                
                # Analizar estructura del CV
                analysis = self._analyze_improved_cv_structure(cv_data)
                
                # Construir resultado compatible
                compatible_result = self._build_improved_compatible_result(cv_data, analysis, result.content)
                
                logger.info("✅ Análisis mejorado completado exitosamente")
                return compatible_result
                
            finally:
                # Limpiar archivo temporal
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
                    
        except Exception as e:
            logger.error(f"❌ Error en análisis mejorado: {e}")
            return {
                "error": f"Error en análisis mejorado: {str(e)}",
                "cv_info": {},
                "analysis": {},
                "raw_text": ""
            }
    
    def _extract_improved_structured_data(self, result) -> Dict[str, Any]:
        """Extrae datos estructurados con parsing mejorado y layout-aware"""
        content = getattr(result, "content", "") or ""

        # 1) Bloques y secciones basadas en layout (columnas + headings)
        blocks = self._extract_layout_blocks(result)
        sections = self._segment_sections_by_headings(blocks)
        tables = self._extract_tables(result)

        # Idiomas: intentar por secciones; si no hay, usar fallback por contenido completo
        langs = self._extract_languages_from_sections(sections)
        if not langs:
            langs = self._extract_improved_languages(result)

        return {
            "contacto": self._extract_contact_from_layout(blocks, tables),
            "experiencia": self._extract_experience_from_sections(sections),
            "educacion": self._extract_education_from_sections(sections),
            "habilidades_tecnicas": self._extract_improved_skills(result),
            "idiomas": langs,
            "proyectos": self._extract_improved_projects(result),
            "resumen_profesional": " ".join(sections.get("resumen", [])).strip() or self._extract_improved_profile(result),
            "raw_content": content,
        }
    
    def _extract_improved_contact_info(self, result) -> Dict[str, str]:
        """Conservado como fallback; la vía principal ahora es _extract_contact_from_layout."""
        # Mantener compatibilidad si en algún flujo falta layout
        contact = {}
        content = getattr(result, "content", "") or ""
        email_match = re.findall(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", content)
        if email_match:
            contact["email"] = email_match[0]
        phone_match = re.findall(r"(?:\+?\d{1,3}[\s.-]?)?(?:\(?\d{2,3}\)?[\s.-]?){2,4}\d{2,4}", content)
        if phone_match:
            contact["phone"] = phone_match[0]
        linkedin_match = re.findall(r"linkedin\.com/\S+", content, re.IGNORECASE)
        if linkedin_match:
            contact["linkedin"] = linkedin_match[0]
        return contact
    
    def _extract_improved_experience(self, result) -> List[Dict[str, str]]:
        """Extrae experiencia laboral con patrones mejorados"""
        experience = []
        content = result.content
        
        # Palabras clave mejoradas para sección de experiencia
        experience_keywords = [
            "experiencia", "laboral", "trabajo", "empleo", "profesional",
            "carrera", "historial", "background", "work experience",
            "employment", "professional experience", "career", "voluntariado",
            "voluntario", "volunteer", "volunteering", "prácticas", "practicas",
            "internship", "beca", "scholarship", "colaboración", "colaboracion"
        ]
        
        # Buscar sección de experiencia
        experience_section = self._find_section_content(content, experience_keywords, [
            "educación", "formación", "académica", "estudios", "education",
            "habilidades", "skills", "competencias", "tecnologías", "abilities",
            "proyectos", "portfolio", "projects", "idiomas", "languages"
        ])
        
        # Si no encontramos sección específica, buscar en todo el contenido
        if not experience_section:
            # Buscar experiencias dispersas en el CV
            experience_section = self._find_scattered_experiences(content)
        
        if experience_section:
            # Dividir en experiencias individuales
            experiences = self._split_experiences(experience_section)
            
            for exp_text in experiences:
                exp_data = self._parse_experience_entry(exp_text)
                if exp_data:
                    experience.append(exp_data)
        
        return experience

    # ===== NUEVO: utilidades layout-aware =====
    def _get_bbox_from_polygon(self, polygon) -> Tuple[float, float, float, float]:
        xs = [p.x for p in polygon]
        ys = [p.y for p in polygon]
        return (min(xs), min(ys), max(xs), max(ys))

    def _is_probable_heading(self, txt: str) -> bool:
        t = (txt or "").strip()
        if not t or len(t) > 80:
            return False
        if t.endswith(":"):
            return True
        if t.isupper() and not any(ch.isdigit() for ch in t):
            return True
        low = t.lower().strip(":")
        return any(any(k in low for k in keys) for keys in SECTION_TITLES.values())

    def _heading_key(self, txt: str) -> Optional[str]:
        low = (txt or "").lower().strip(":")
        for key, keys in SECTION_TITLES.items():
            if any(k in low for k in keys):
                return key
        return None

    def _extract_layout_blocks(self, result) -> List[Block]:
        blocks: List[Block] = []
        for p, page in enumerate(getattr(result, "pages", []) or []):
            page_blocks: List[Block] = []
            x_mids: List[float] = []
            for line in getattr(page, "lines", []) or []:
                if not getattr(line, "content", None) or not getattr(line, "polygon", None):
                    continue
                xmin, ymin, xmax, ymax = self._get_bbox_from_polygon(line.polygon)
                xmid = (xmin + xmax) / 2.0
                x_mids.append(xmid)
                page_blocks.append(Block(text=line.content.strip(), page=p + 1, bbox=(xmin, ymin, xmax, ymax)))
            col_threshold = None
            if len(x_mids) >= 10:
                xs = sorted(x_mids)
                gaps = [(xs[i + 1] - xs[i], i) for i in range(len(xs) - 1)]
                if gaps:
                    max_gap, idx = max(gaps, key=lambda g: g[0])
                    if max_gap > 40:
                        col_threshold = (xs[idx] + xs[idx + 1]) / 2.0
            for b in page_blocks:
                xmin, ymin, xmax, ymax = b.bbox
                xmid = (xmin + xmax) / 2.0
                b.col = 0 if (col_threshold is None or xmid <= col_threshold) else 1
                b.is_heading = self._is_probable_heading(b.text)
                b.heading_key = self._heading_key(b.text) if b.is_heading else None
                blocks.append(b)
        blocks.sort(key=lambda b: (b.page, b.col, b.bbox[1], b.bbox[0]))
        return blocks

    def _segment_sections_by_headings(self, blocks: List[Block]) -> Dict[str, List[str]]:
        sections: Dict[str, List[str]] = {k: [] for k in SECTION_TITLES.keys()}
        current_key: Optional[str] = None
        for b in blocks:
            if b.is_heading and b.heading_key:
                current_key = b.heading_key
                continue
            if current_key:
                if b.is_heading and b.heading_key:
                    current_key = b.heading_key
                    continue
                t = b.text.strip("•·-— ").replace("  ", " ")
                if t:
                    sections[current_key].append(t)
        return sections

    def _extract_tables(self, result) -> List[Dict[str, Any]]:
        out: List[Dict[str, Any]] = []
        for tb in getattr(result, "tables", []) or []:
            rows: Dict[int, Dict[int, str]] = {}
            for cell in tb.cells:
                rows.setdefault(cell.row_index, {})[cell.column_index] = (cell.content or "").strip()
            ordered: List[List[str]] = []
            for r_idx in sorted(rows.keys()):
                row = rows[r_idx]
                max_c = max(row.keys()) if row else -1
                ordered.append([row.get(c, "") for c in range(max_c + 1)])
            out.append({"rows": ordered})
        return out

    def _table_kv_pairs(self, tables: List[Dict[str, Any]]) -> Dict[str, str]:
        kv: Dict[str, str] = {}
        for t in tables:
            for row in t.get("rows", []):
                if len(row) == 2:
                    k = row[0].strip().lower().strip(":")
                    v = row[1].strip()
                    if k and v and len(k) <= 40:
                        kv[k] = v
        return kv

    # Normalizadores
    def _norm_date(self, txt: str) -> Optional[str]:
        if not dateparser:
            return None
        try:
            d = dateparser.parse(txt, languages=["es", "en"], settings={"PREFER_DAY_OF_MONTH": "first"})
            return d.strftime("%Y-%m") if d else None
        except Exception:
            return None

    def _parse_date_range(self, line: str) -> Tuple[Optional[str], Optional[str], bool]:
        m = DATE_RANGE_RE.search(line or "")
        if not m:
            return (None, None, False)
        start_raw = m.group("start")
        end_raw = m.group("end")
        start = self._norm_date(start_raw) or (re.findall(r"\d{4}", start_raw)[0] if re.findall(r"\d{4}", start_raw) else None)
        current = False
        if re.search(r"(actualidad|presente|now|current)", end_raw, re.IGNORECASE):
            end = None
            current = True
        else:
            end = self._norm_date(end_raw) or (re.findall(r"\d{4}", end_raw)[0] if re.findall(r"\d{4}", end_raw) else None)
        return (start, end, current)

    def _norm_phones(self, texts: List[str], region: str = "ES") -> List[str]:
        found: set[str] = set()
        for t in texts or []:
            for m in re.findall(r"(?:\+?\d[\d\s().-]{6,})", t):
                try:
                    if phonenumbers:
                        num = phonenumbers.parse(m, region)
                        if phonenumbers.is_valid_number(num):
                            found.add(phonenumbers.format_number(num, phonenumbers.PhoneNumberFormat.E164))
                except Exception:
                    continue
        return sorted(found)
    
    def _find_scattered_experiences(self, content: str) -> str:
        """Busca experiencias laborales dispersas en el contenido del CV"""
        experience_lines = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            line_stripped = line.strip()
            if not line_stripped:
                continue
            
            # Detectar líneas que parecen experiencia laboral
            if self._looks_like_experience_line(line_stripped):
                # Agregar la línea actual y las siguientes hasta encontrar otra experiencia
                experience_lines.append(line_stripped)
                
                # Buscar líneas relacionadas (descripción del trabajo)
                j = i + 1
                while j < len(lines) and j < i + 5:  # Máximo 5 líneas de descripción
                    next_line = lines[j].strip()
                    if next_line and not self._looks_like_new_experience(next_line):
                        experience_lines.append(next_line)
                        j += 1
                    else:
                        break
                
                experience_lines.append("")  # Separador
        
        return '\n'.join(experience_lines)
    
    def _looks_like_experience_line(self, line: str) -> bool:
        """Determina si una línea parece ser una experiencia laboral"""
        # Patrones que indican experiencia laboral
        patterns = [
            r'\d{4}\s*[-–]\s*\d{4}',  # 2020 - 2023
            r'\d{4}\s*[-–]\s*(?:actualidad|presente|now)',  # 2020 - actualidad
            r'\b(?:ene|feb|mar|abr|may|jun|jul|ago|sep|oct|nov|dic)\s+\d{4}',  # Ene 2020
            r'\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\s+\d{4}',  # Jan 2020
        ]
        
        # Verificar patrones de fecha
        for pattern in patterns:
            if re.search(pattern, line.lower()):
                return True
        
        # Verificar si contiene palabras clave de experiencia
        experience_indicators = [
            "voluntario", "volunteer", "becario", "intern", "practicante", "trainee",
            "colaborador", "collaborator", "presidente", "president", "cofundador", "co-founder",
            "fundador", "founder", "responsable", "responsible", "encargado", "in charge"
        ]
        
        line_lower = line.lower()
        return any(indicator in line_lower for indicator in experience_indicators)
    
    def _looks_like_new_experience(self, line: str) -> bool:
        """Determina si una línea indica el inicio de una nueva experiencia"""
        # Patrones que indican nueva experiencia
        patterns = [
            r'^\d{4}\s*[-–]',  # Empieza con año
            r'^\b(?:ene|feb|mar|abr|may|jun|jul|ago|sep|oct|nov|dic)\s+\d{4}',  # Empieza con mes año
            r'^\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\s+\d{4}',  # Empieza con mes año
        ]
        
        for pattern in patterns:
            if re.match(pattern, line.lower()):
                return True
        
        # Verificar si es una empresa (mayúsculas, sin números)
        if re.match(r'^[A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑ\s&.,-]+$', line) and len(line) > 3:
            return True
        
        return False
    
    def _extract_improved_education(self, result) -> List[Dict[str, str]]:
        """Extrae educación con patrones mejorados"""
        education = []
        content = result.content
        
        # Palabras clave mejoradas para sección de educación
        education_keywords = [
            "educación", "formación", "académica", "estudios", "education",
            "academic", "training", "formación académica", "estudios académicos"
        ]
        
        # Buscar sección de educación
        education_section = self._find_section_content(content, education_keywords, [
            "experiencia", "laboral", "trabajo", "empleo", "experience",
            "habilidades", "skills", "competencias", "tecnologías", "abilities",
            "proyectos", "portfolio", "projects", "idiomas", "languages"
        ])
        
        if education_section:
            # Dividir en estudios individuales
            studies = self._split_education_entries(education_section)
            
            for study_text in studies:
                study_data = self._parse_education_entry(study_text)
                if study_data:
                    education.append(study_data)
        
        return education
    
    def _extract_improved_skills(self, result) -> List[str]:
        """Extrae habilidades técnicas con patrones mejorados"""
        skills = []
        content = result.content
        
        # Palabras clave mejoradas para sección de habilidades
        skills_keywords = [
            "habilidades", "skills", "competencias", "tecnologías", "abilities",
            "technical skills", "programming languages", "frameworks",
            "tools", "software", "technologies", "lenguajes", "herramientas"
        ]
        
        # Buscar sección de habilidades
        skills_section = self._find_section_content(content, skills_keywords, [
            "experiencia", "laboral", "trabajo", "empleo", "experience",
            "educación", "formación", "académica", "estudios", "education",
            "proyectos", "portfolio", "projects", "idiomas", "languages"
        ])
        
        # Lista MUY expandida de tecnologías y herramientas
        tech_keywords = [
            # Microsoft Office Suite
            "microsoft office", "office", "word", "excel", "powerpoint", "power point", "access", "outlook", "onenote", "sharepoint", "teams", "skype",
            
            # Adobe Creative Suite
            "adobe", "photoshop", "illustrator", "indesign", "after effects", "premiere", "premiere pro", "lightroom", "acrobat", "xd", "dreamweaver", "flash", "fireworks",
            
            # Lenguajes de programación
            "javascript", "js", "typescript", "ts", "python", "py", "java", "c++", "c#", "php", "ruby", "go", "rust", "swift", "kotlin", "scala", "r", "matlab", "perl", "bash", "shell", "powershell",
            
            # Frameworks frontend
            "react", "angular", "vue", "vue.js", "svelte", "next.js", "nuxt.js", "gatsby", "ember", "backbone", "jquery",
            
            # Frameworks backend
            "node.js", "nodejs", "express", "django", "flask", "fastapi", "spring", "laravel", "rails", "asp.net", "dotnet", "symfony", "codeigniter", "yii", "zend",
            
            # Bases de datos
            "sql", "mysql", "postgresql", "postgres", "mongodb", "redis", "oracle", "sqlite", "mariadb", "sql server", "mssql", "db2", "cassandra", "neo4j", "elasticsearch", "base de datos", "database",
            
            # Frontend
            "html", "html5", "css", "css3", "bootstrap", "tailwind", "sass", "scss", "less", "stylus", "webpack", "vite", "parcel", "gulp", "grunt", "babel",
            
            # DevOps y Cloud
            "git", "github", "gitlab", "bitbucket", "docker", "kubernetes", "k8s", "aws", "amazon web services", "azure", "gcp", "google cloud", "heroku", "vercel", "netlify", "digitalocean", "linode",
            
            # Machine Learning y Data Science
            "machine learning", "ml", "ai", "artificial intelligence", "data science", "analytics", "tensorflow", "pytorch", "scikit-learn", "sklearn", "pandas", "numpy", "matplotlib", "seaborn", "plotly", "jupyter", "r studio", "spss", "sas", "stata",
            
            # Herramientas de gestión y colaboración
            "jira", "confluence", "slack", "microsoft teams", "trello", "asana", "basecamp", "notion", "monday.com", "clickup", "linear", "github projects",
            
            # Herramientas de diseño
            "figma", "sketch", "invision", "marvel", "principle", "framer", "webflow", "bubble", "wix", "squarespace", "wordpress", "drupal", "joomla",
            
            # CRM y ERP
            "crm", "salesforce", "hubspot", "pipedrive", "zoho", "sap", "oracle erp", "microsoft dynamics", "odoo", "erp", "enterprise resource planning",
            
            # Herramientas de análisis
            "google analytics", "analytics", "mixpanel", "amplitude", "hotjar", "crazy egg", "optimizely", "ab testing", "a/b testing",
            
            # Herramientas de marketing
            "mailchimp", "sendgrid", "constant contact", "campaign monitor", "klaviyo", "hubspot marketing", "marketo", "pardot",
            
            # Herramientas de productividad
            "notion", "evernote", "onenote", "roam research", "obsidian", "logseq", "bear", "ulysses", "scrivener",
            
            # Herramientas de comunicación
            "zoom", "webex", "gotomeeting", "bluejeans", "discord", "telegram", "whatsapp business", "slack", "microsoft teams",
            
            # Herramientas de desarrollo
            "vscode", "visual studio", "intellij", "eclipse", "sublime text", "atom", "vim", "emacs", "notepad++", "brackets",
            
            # Metodologías y frameworks
            "agile", "scrum", "kanban", "devops", "ci/cd", "tdd", "bdd", "lean", "six sigma", "waterfall", "prince2", "pmp",
            
            # Herramientas de testing
            "selenium", "cypress", "jest", "mocha", "jasmine", "phpunit", "pytest", "junit", "testng", "postman", "insomnia", "soapui",
            
            # Herramientas de monitoreo
            "new relic", "datadog", "splunk", "elk stack", "elasticsearch", "logstash", "kibana", "grafana", "prometheus", "nagios", "zabbix",
            
            # Herramientas de seguridad
            "wireshark", "nmap", "metasploit", "burp suite", "owasp", "penetration testing", "vulnerability assessment",
            
            # Herramientas de gestión de proyectos
            "microsoft project", "ms project", "smartsheet", "wrike", "teamgantt", "liquidplanner", "project management",
            
            # Herramientas de contabilidad y finanzas
            "quickbooks", "xero", "sage", "freshbooks", "wave", "mint", "quicken", "turbotax", "excel avanzado", "power bi", "tableau", "qlikview",
            
            # Herramientas de recursos humanos
            "workday", "bamboo hr", "gusto", "zenefits", "adp", "paychex", "greenhouse", "lever", "breezy hr", "hr software",
            
            # Herramientas de ventas
            "salesforce", "hubspot crm", "pipedrive", "zoho crm", "freshsales", "insightly", "nimble", "sales software",
            
            # Herramientas de soporte al cliente
            "zendesk", "freshdesk", "intercom", "help scout", "desk.com", "kayako", "livechat", "chat software",
            
            # Herramientas de e-commerce
            "shopify", "woocommerce", "magento", "prestashop", "opencart", "bigcommerce", "squarespace commerce", "ecommerce",
            
            # Herramientas de gestión de contenido
            "wordpress", "drupal", "joomla", "typo3", "concrete5", "umbraco", "sitecore", "content management", "cms",
            
            # Herramientas de automatización
            "zapier", "ifttt", "integromat", "automation", "workflow", "process automation", "rpa", "robotic process automation",
            
            # Herramientas de video y multimedia
            "premiere pro", "after effects", "final cut pro", "davinci resolve", "camtasia", "screencast-o-matic", "video editing",
            
            # Herramientas de audio
            "audacity", "pro tools", "logic pro", "garageband", "ableton", "fl studio", "audio editing", "podcast",
            
            # Herramientas de 3D y CAD
            "autocad", "solidworks", "fusion 360", "blender", "maya", "3ds max", "cinema 4d", "sketchup", "3d modeling", "cad",
            
            # Herramientas de gestión de archivos
            "dropbox", "google drive", "onedrive", "box", "mega", "pcloud", "icloud", "file management", "cloud storage",
            
            # Herramientas de backup y recuperación
            "backup", "recovery", "veeam", "acronis", "carbonite", "crashplan", "backblaze", "data protection",
            
            # Herramientas de virtualización
            "vmware", "virtualbox", "hyper-v", "xen", "kvm", "virtualization", "virtual machines", "vms",
            
            # Herramientas de networking
            "cisco", "juniper", "arista", "networking", "routing", "switching", "firewall", "vpn", "wireshark", "packet tracer",
            
            # Herramientas de gestión de servidores
            "linux", "ubuntu", "centos", "red hat", "debian", "windows server", "server administration", "system administration",
            
            # Herramientas de gestión de bases de datos
            "database administration", "dba", "database management", "data modeling", "erwin", "powerdesigner", "mysql workbench", "pgadmin",
            
            # Herramientas de business intelligence
            "power bi", "tableau", "qlikview", "qlik sense", "microstrategy", "business intelligence", "bi", "data visualization", "dashboard",
            
            # Herramientas de gestión de APIs
            "rest api", "graphql", "soap", "api management", "swagger", "openapi", "postman", "insomnia", "api testing",
            
            # Herramientas de gestión de contenedores
            "docker", "kubernetes", "rancher", "openshift", "docker swarm", "container orchestration", "microservices",
            
            # Herramientas de gestión de configuración
            "ansible", "chef", "puppet", "terraform", "configuration management", "infrastructure as code", "iac",
            
            # Herramientas de gestión de logs
            "log management", "log analysis", "centralized logging", "log aggregation", "log monitoring",
            
            # Herramientas de gestión de incidentes
            "incident management", "pagerduty", "opsgenie", "victorops", "alerting", "on-call", "incident response",
            
            # Herramientas de gestión de cambios
            "change management", "release management", "deployment", "continuous deployment", "blue-green deployment",
            
            # Herramientas de gestión de dependencias
            "npm", "yarn", "composer", "pip", "maven", "gradle", "nuget", "package management", "dependency management",
            
            # Herramientas de gestión de versiones
            "git", "svn", "mercurial", "version control", "source control", "revision control",
            
            # Herramientas de gestión de documentación
            "confluence", "notion", "gitbook", "readme", "documentation", "technical writing", "api documentation",
            
            # Herramientas de gestión de código
            "code review", "pull request", "merge request", "code quality", "sonarqube", "code coverage", "static analysis",
            
            # Herramientas de gestión de seguridad
            "security scanning", "vulnerability scanning", "penetration testing", "security audit", "compliance", "gdpr", "sox",
            
            # Herramientas de gestión de rendimiento
            "performance monitoring", "apm", "application performance monitoring", "load testing", "stress testing", "jmeter", "gatling",
            
            # Herramientas de gestión de accesibilidad
            "accessibility", "wcag", "ada compliance", "screen reader", "accessibility testing", "inclusive design",
            
            # Herramientas de gestión de localización
            "localization", "internationalization", "i18n", "l10n", "translation", "multilingual", "globalization",
            
            # Herramientas de gestión de SEO
            "seo", "search engine optimization", "google search console", "semrush", "ahrefs", "moz", "keyword research",
            
            # Herramientas de gestión de redes sociales
            "social media management", "hootsuite", "buffer", "sprout social", "social media marketing", "community management",
            
            # Herramientas de gestión de eventos
            "event management", "eventbrite", "meetup", "webinar", "virtual events", "hybrid events", "event planning",
            
            # Herramientas de gestión de inventario
            "inventory management", "warehouse management", "supply chain", "logistics", "procurement", "purchase order",
            
            # Herramientas de gestión de calidad
            "quality assurance", "qa", "testing", "test automation", "quality management", "iso 9001", "six sigma",
            
            # Herramientas de gestión de riesgos
            "risk management", "compliance", "audit", "governance", "risk assessment", "business continuity",
            
            # Herramientas de gestión de conocimiento
            "knowledge management", "knowledge base", "wiki", "documentation", "training", "learning management system", "lms"
        ]
        
        # Buscar tecnologías en TODO el contenido del CV, no solo en la sección de habilidades
        content_lower = content.lower()
        
        # Buscar tecnologías en el texto completo
        for tech in tech_keywords:
            if tech in content_lower:
                # Normalizar el nombre de la tecnología
                normalized_tech = self._normalize_tech_name(tech)
                if normalized_tech not in skills:
                    skills.append(normalized_tech)
        
        # También buscar en la sección específica de habilidades si existe
        if skills_section:
            for line in skills_section.split('\n'):
                line_lower = line.lower()
                for tech in tech_keywords:
                    if tech in line_lower:
                        # Normalizar el nombre de la tecnología
                        normalized_tech = self._normalize_tech_name(tech)
                        if normalized_tech not in skills:
                            skills.append(normalized_tech)
        
        return skills
    
    def _extract_improved_languages(self, result) -> List[Dict[str, str]]:
        """Extrae idiomas con patrones mejorados"""
        languages = []
        content = result.content
        
        # Palabras clave para sección de idiomas
        language_keywords = [
            "idiomas", "languages", "idioma", "language", "lenguas"
        ]
        
        # Buscar sección de idiomas
        language_section = self._find_section_content(content, language_keywords, [
            "experiencia", "educación", "habilidades", "proyectos"
        ])
        
        if language_section:
            # Idiomas comunes
            language_names = [
                "español", "castellano", "inglés", "francés", "alemán", "italiano", "portugués",
                "catalán", "euskera", "gallego", "chino", "japonés", "coreano", "ruso", "árabe"
            ]
            
            # Niveles de idioma
            levels = ["nativo", "bilingüe", "avanzado", "intermedio", "básico", "principiante"]
            
            for line in language_section.split('\n'):
                line_lower = line.lower()
                for lang in language_names:
                    if lang in line_lower:
                        level = "intermedio"  # Por defecto
                        for lvl in levels:
                            if lvl in line_lower:
                                level = lvl
                                break
                        
                        languages.append({
                            "idioma": lang.title(),
                            "nivel": level
                        })
                        break
        
        return languages

    def _extract_languages_from_sections(self, sections: Dict[str, List[str]]) -> List[Dict[str, str]]:
        """Extrae idiomas a partir de las secciones segmentadas por headings.

        Esta función corrige el fallo reportado cuando se invoca
        `_extract_languages_from_sections` inexistente. Implementa un parser
        sencillo y robusto sobre las líneas de la sección `idiomas`.
        """
        try:
            lines = sections.get("idiomas", []) or []
            if not lines:
                return []

            # Listados básicos de idiomas y niveles
            language_names = [
                "español", "castellano", "inglés", "francés", "alemán", "italiano",
                "portugués", "catalán", "euskera", "gallego", "chino", "japonés",
                "coreano", "ruso", "árabe"
            ]
            # Aceptar abreviaturas tipo B2/C1/C2
            level_aliases = {
                "nativo": "nativo",
                "bilingüe": "bilingüe",
                "bilingue": "bilingüe",
                "c2": "bilingüe",
                "c1": "avanzado",
                "b2": "intermedio",
                "b1": "intermedio",
                "a2": "básico",
                "a1": "básico",
                "avanzado": "avanzado",
                "intermedio": "intermedio",
                "medio": "intermedio",
                "básico": "básico",
                "basico": "básico",
            }

            found: List[Dict[str, str]] = []
            for raw in lines:
                t = (raw or "").strip().lower()
                if not t:
                    continue
                # Buscar nombre de idioma
                idioma: Optional[str] = None
                for lang in language_names:
                    if lang in t:
                        idioma = lang.title()
                        break
                if not idioma:
                    # Patrones genéricos con dos puntos p.ej. "Inglés: B2"
                    m = re.search(r"^([a-záéíóúñ]+)\s*[:|-]", t)
                    if m:
                        idioma = m.group(1).title()
                if not idioma:
                    continue

                # Buscar nivel
                nivel = "intermedio"
                for key, norm in level_aliases.items():
                    if re.search(rf"\b{re.escape(key)}\b", t):
                        nivel = norm
                        break

                found.append({"idioma": idioma, "nivel": nivel})

            # Evitar duplicados conservando el primero
            unique: List[Dict[str, str]] = []
            seen = set()
            for item in found:
                k = (item.get("idioma", ""), item.get("nivel", ""))
                if k in seen:
                    continue
                seen.add(k)
                unique.append(item)

            return unique
        except Exception:
            return []

    # ===== NUEVO: extractores basados en secciones =====
    def _extract_contact_from_layout(self, blocks: List[Block], tables: List[Dict[str, Any]]) -> Dict[str, Any]:
        kv = self._table_kv_pairs(tables)
        candidates: List[str] = []
        if kv:
            candidates.extend(list(kv.values())[:20])
        left_lines = [b.text for b in blocks if b.col == 0][:30]
        candidates.extend(left_lines)
        # emails
        emails = []
        try:
            emails = sorted(set(re.findall(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", "\n".join(candidates))))
        except Exception:
            emails = []
        # phones
        phones = self._norm_phones(candidates, region="ES")
        # linkedin
        linkedin = None
        for t in candidates:
            if "linkedin." in t.lower():
                u = t.strip()
                if not u.startswith("http"):
                    u = "https://" + u.lstrip("/")
                linkedin = u
                break
        # ubicación simple (heurística España)
        location = None
        for t in candidates:
            if re.search(r"madrid|barcelona|valencia|sevilla|bilbao|coruñ|león|zaragoza|vigo|alicante|granada|málaga|ourense|ponferrada", t, re.IGNORECASE):
                location = t.strip()
                break
        return {"email": emails[0] if emails else "", "emails": emails, "phones": phones, "linkedin": linkedin or "", "location": location or ""}

    def _extract_experience_from_sections(self, sections: Dict[str, List[str]]) -> List[Dict[str, Any]]:
        out: List[Dict[str, Any]] = []
        lines = sections.get("experiencia", [])
        buff: List[str] = []

        def flush():
            if not buff:
                return
            chunk = " ".join(buff)
            start, end, current = self._parse_date_range(chunk)
            company, position = None, None
            if buff:
                head = buff[0]
                if re.search(r"\s[-–]\s", head):
                    parts = re.split(r"\s[-–]\s", head, maxsplit=1)
                    if len(parts) == 2:
                        company, position = parts[0].strip(), parts[1].strip()
                if not company and head.upper() == head and not re.search(r"\d", head):
                    company = head.title()
                if not position and len(buff) > 1:
                    position = buff[1].strip()
            desc = [ln for ln in buff[1:] if ln]
            out.append({
                "company": company or "",
                "position": position or "",
                "start_date": start,
                "end_date": end,
                "current": current,
                "description": " ".join(desc).strip(),
            })
            buff.clear()

        for ln in lines:
            if not ln:
                continue
            if DATE_RANGE_RE.search(ln) and buff:
                flush()
            buff.append(ln)
            if len(buff) > 12:
                flush()
        flush()
        return [e for e in out if e.get("company") or e.get("position") or e.get("start_date")]

    def _extract_education_from_sections(self, sections: Dict[str, List[str]]) -> List[Dict[str, Any]]:
        out: List[Dict[str, Any]] = []
        for ln in sections.get("educacion", []):
            degree = None
            institution = None
            start, end, _ = self._parse_date_range(ln)
            if re.search(r"grado|licenciatura|máster|master|doctorado|phd|ingenier", ln, re.IGNORECASE):
                degree = ln
            if re.search(r"universidad|university|escuela|instituto|facultad|eae|esade|uned|uam|upm|upv|uv|uca|uma", ln, re.IGNORECASE):
                institution = ln
            if degree or institution or start or end:
                out.append({
                    "degree": degree or "",
                    "institution": institution or "",
                    "start_date": start,
                    "end_date": end,
                })
        merged: List[Dict[str, Any]] = []
        for e in out:
            if merged and not e["degree"] and merged[-1]["degree"] and not merged[-1].get("institution") and e.get("institution"):
                merged[-1]["institution"] = e["institution"]
                merged[-1]["start_date"] = merged[-1].get("start_date") or e.get("start_date")
                merged[-1]["end_date"] = merged[-1].get("end_date") or e.get("end_date")
            else:
                merged.append(e)
        return merged
    
    def _extract_improved_projects(self, result) -> List[Dict[str, str]]:
        """Extrae proyectos con patrones mejorados"""
        projects = []
        content = result.content
        
        # Palabras clave para sección de proyectos
        project_keywords = [
            "proyectos", "projects", "portfolio", "trabajos", "works",
            "proyectos destacados", "featured projects"
        ]
        
        # Buscar sección de proyectos
        project_section = self._find_section_content(content, project_keywords, [
            "experiencia", "educación", "habilidades", "idiomas"
        ])
        
        if project_section:
            # Dividir en proyectos individuales
            project_entries = self._split_project_entries(project_section)
            
            for project_text in project_entries:
                project_data = self._parse_project_entry(project_text)
                if project_data:
                    projects.append(project_data)
        
        return projects
    
    def _extract_improved_profile(self, result) -> str:
        """Extrae perfil profesional"""
        content = result.content
        
        # Buscar sección de perfil
        profile_keywords = [
            "perfil", "profile", "resumen", "summary", "objetivo", "objective",
            "descripción", "description", "sobre mí", "about me"
        ]
        
        profile_section = self._find_section_content(content, profile_keywords, [
            "experiencia", "educación", "habilidades", "proyectos"
        ])
        
        return profile_section if profile_section else ""
    
    # Métodos auxiliares mejorados
    def _find_section_content(self, content: str, start_keywords: List[str], end_keywords: List[str]) -> str:
        """Encuentra el contenido de una sección específica"""
        lines = content.split('\n')
        section_content = ""
        in_section = False
        
        for line in lines:
            line_lower = line.lower().strip()
            
            # Verificar si estamos entrando en la sección
            if not in_section:
                for keyword in start_keywords:
                    if keyword in line_lower:
                        in_section = True
                        break
            
            # Verificar si estamos saliendo de la sección
            elif in_section:
                for keyword in end_keywords:
                    if keyword in line_lower:
                        return section_content.strip()
                
                section_content += line + '\n'
        
        return section_content.strip()
    
    def _split_experiences(self, experience_section: str) -> List[str]:
        """Divide la sección de experiencia en experiencias individuales"""
        experiences = []
        current_exp = ""
        
        for line in experience_section.split('\n'):
            line = line.strip()
            
            # Detectar nueva experiencia (fechas, empresas, etc.)
            if self._is_new_experience(line):
                if current_exp:
                    experiences.append(current_exp.strip())
                current_exp = line
            else:
                current_exp += "\n" + line
        
        if current_exp:
            experiences.append(current_exp.strip())
        
        return experiences
    
    def _is_new_experience(self, line: str) -> bool:
        """Determina si una línea indica una nueva experiencia"""
        # Patrones para detectar nueva experiencia
        patterns = [
            r'\d{4}\s*[-–]\s*\d{4}',  # 2020 - 2023
            r'\d{4}\s*[-–]\s*actualidad',  # 2020 - actualidad
            r'\d{4}\s*[-–]\s*presente',  # 2020 - presente
            r'\b(ene|feb|mar|abr|may|jun|jul|ago|sep|oct|nov|dic)\s+\d{4}',  # Ene 2020
            r'\b(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\s+\d{4}',  # Jan 2020
        ]
        
        for pattern in patterns:
            if re.search(pattern, line.lower()):
                return True
        
        # Verificar si es una empresa (mayúsculas, sin números)
        if re.match(r'^[A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑ\s&.,-]+$', line) and len(line) > 3:
            return True
        
        return False
    
    def _parse_experience_entry(self, exp_text: str) -> Optional[Dict[str, str]]:
        """Parsea una entrada de experiencia individual"""
        if not exp_text.strip():
            return None
        
        exp_data = {}
        lines = exp_text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Buscar período
            period_patterns = [
                r'(\d{4}\s*[-–]\s*\d{4})',
                r'(\d{4}\s*[-–]\s*(?:actualidad|presente))',
                r'(\b(?:ene|feb|mar|abr|may|jun|jul|ago|sep|oct|nov|dic)\s+\d{4})',
                r'(\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\s+\d{4})'
            ]
            
            for pattern in period_patterns:
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    exp_data['period'] = match.group(1)
                    break
            
            # Buscar empresa (líneas en mayúsculas)
            if re.match(r'^[A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑ\s&.,-]+$', line) and len(line) > 3:
                exp_data['company'] = line
            
            # Buscar puesto (contiene palabras clave de puestos)
            position_keywords = [
                "desarrollador", "developer", "analista", "analyst", "ingeniero", "engineer",
                "consultor", "consultant", "manager", "director", "coordinador", "coordinator",
                "especialista", "specialist", "arquitecto", "architect", "diseñador", "designer",
                "voluntario", "volunteer", "becario", "intern", "practicante", "trainee",
                "colaborador", "collaborator", "asistente", "assistant", "ayudante", "helper",
                "presidente", "president", "cofundador", "co-founder", "fundador", "founder",
                "responsable", "responsible", "encargado", "in charge", "supervisor", "supervisor"
            ]
            
            if any(keyword in line.lower() for keyword in position_keywords):
                exp_data['position'] = line
        
        # Si no encontramos descripción, usar todo el texto
        if 'description' not in exp_data:
            exp_data['description'] = exp_text
        
        return exp_data if len(exp_data) > 1 else None
    
    def _split_education_entries(self, education_section: str) -> List[str]:
        """Divide la sección de educación en estudios individuales"""
        studies = []
        current_study = ""
        
        for line in education_section.split('\n'):
            line = line.strip()
            
            # Detectar nuevo estudio
            if self._is_new_education(line):
                if current_study:
                    studies.append(current_study.strip())
                current_study = line
            else:
                current_study += "\n" + line
        
        if current_study:
            studies.append(current_study.strip())
        
        return studies
    
    def _is_new_education(self, line: str) -> bool:
        """Determina si una línea indica una nueva educación"""
        education_keywords = [
            "grado", "licenciatura", "máster", "doctorado", "ingeniería",
            "degree", "bachelor", "master", "phd", "engineering"
        ]
        
        return any(keyword in line.lower() for keyword in education_keywords)
    
    def _parse_education_entry(self, study_text: str) -> Optional[Dict[str, str]]:
        """Parsea una entrada de educación individual"""
        if not study_text.strip():
            return None
        
        study_data = {}
        lines = study_text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Buscar título
            title_keywords = [
                "grado", "licenciatura", "máster", "doctorado", "ingeniería",
                "degree", "bachelor", "master", "phd", "engineering"
            ]
            
            if any(keyword in line.lower() for keyword in title_keywords):
                study_data['title'] = line
            
            # Buscar institución
            institution_keywords = [
                "universidad", "instituto", "escuela", "university", "institute", "school",
                "eneb", "euroinnova", "foesco", "academia del transportista", "eae", "esade", "uned", "uce3m",
                "centro", "academia", "fundación", "asociación", "colegio", "facultad", "departamento"
            ]
            
            if any(keyword in line.lower() for keyword in institution_keywords):
                study_data['institution'] = line
            
            # Buscar año
            year_match = re.search(r'\b(19|20)\d{2}\b', line)
            if year_match:
                study_data['year'] = year_match.group(0)
        
        return study_data if len(study_data) > 1 else None
    
    def _split_project_entries(self, project_section: str) -> List[str]:
        """Divide la sección de proyectos en proyectos individuales"""
        projects = []
        current_project = ""
        
        for line in project_section.split('\n'):
            line = line.strip()
            
            # Detectar nuevo proyecto (líneas que empiezan con mayúsculas)
            if re.match(r'^[A-ZÁÉÍÓÚÑ]', line) and len(line) > 5:
                if current_project:
                    projects.append(current_project.strip())
                current_project = line
            else:
                current_project += "\n" + line
        
        if current_project:
            projects.append(current_project.strip())
        
        return projects
    
    def _parse_project_entry(self, project_text: str) -> Optional[Dict[str, str]]:
        """Parsea una entrada de proyecto individual"""
        if not project_text.strip():
            return None
        
        project_data = {}
        lines = project_text.split('\n')
        
        # Primera línea como nombre del proyecto
        if lines:
            project_data['nombre'] = lines[0].strip()
        
        # Resto como descripción
        if len(lines) > 1:
            project_data['descripcion'] = '\n'.join(lines[1:]).strip()
        
        # Buscar tecnologías en la descripción
        if 'descripcion' in project_data:
            tech_keywords = [
                "javascript", "python", "react", "node", "sql", "mongodb", "aws", "docker"
            ]
            found_techs = []
            for tech in tech_keywords:
                if tech in project_data['descripcion'].lower():
                    found_techs.append(tech.title())
            
            if found_techs:
                project_data['tecnologias'] = found_techs
        
        return project_data
    
    def _normalize_tech_name(self, tech: str) -> str:
        """Normaliza el nombre de una tecnología"""
        tech_map = {
            "js": "JavaScript",
            "ts": "TypeScript",
            "py": "Python",
            "vue.js": "Vue.js",
            "next.js": "Next.js",
            "nuxt.js": "Nuxt.js",
            "node.js": "Node.js",
            "asp.net": "ASP.NET",
            "dotnet": ".NET",
            "postgresql": "PostgreSQL",
            "postgres": "PostgreSQL",
            "k8s": "Kubernetes",
            "ml": "Machine Learning",
            "ai": "Artificial Intelligence"
        }
        
        return tech_map.get(tech.lower(), tech.title())
    
    def _analyze_improved_cv_structure(self, cv_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analiza la estructura del CV con métricas mejoradas"""
        analysis = {}
        
        # Análisis de completitud
        sections = ['contacto', 'experiencia', 'educacion', 'habilidades_tecnicas', 'idiomas']
        completed_sections = sum(1 for section in sections if cv_data.get(section))
        analysis['completitud'] = f"{completed_sections}/{len(sections)} secciones completadas"
        
        # Análisis de experiencia
        experience = cv_data.get('experiencia', [])
        analysis['experiencia_count'] = len(experience)
        analysis['experiencia_quality'] = 'buena' if len(experience) >= 2 else 'regular'
        
        # Análisis de educación
        education = cv_data.get('educacion', [])
        analysis['educacion_count'] = len(education)
        analysis['educacion_quality'] = 'buena' if len(education) >= 1 else 'regular'
        
        # Análisis de habilidades
        skills = cv_data.get('habilidades_tecnicas', [])
        analysis['habilidades_count'] = len(skills)
        analysis['habilidades_quality'] = 'excelente' if len(skills) >= 10 else 'buena' if len(skills) >= 5 else 'regular'
        
        # Análisis de idiomas
        languages = cv_data.get('idiomas', [])
        analysis['idiomas_count'] = len(languages)
        analysis['idiomas_quality'] = 'buena' if len(languages) >= 2 else 'regular'
        
        # Calificación general
        scores = []
        if len(experience) >= 2: scores.append(100)
        elif len(experience) >= 1: scores.append(70)
        else: scores.append(30)
        
        if len(education) >= 1: scores.append(100)
        else: scores.append(50)
        
        if len(skills) >= 5: scores.append(100)
        elif len(skills) >= 2: scores.append(70)
        else: scores.append(30)
        
        if len(languages) >= 2: scores.append(100)
        elif len(languages) >= 1: scores.append(70)
        else: scores.append(30)
        
        avg_score = sum(scores) / len(scores) if scores else 0
        analysis['puntuacion_general'] = round(avg_score, 1)
        analysis['nivel'] = 'excelente' if avg_score >= 85 else 'bueno' if avg_score >= 70 else 'regular'
        
        return analysis
    
    def _build_improved_compatible_result(self, cv_data: Dict[str, Any], analysis: Dict[str, Any], raw_text: str) -> Dict[str, Any]:
        """Construye resultado compatible con el formato esperado"""
        try:
            # Validar que los datos sean válidos
            if not isinstance(cv_data, dict):
                logger.warning("⚠️ cv_data no es un diccionario válido")
                cv_data = {}
            
            if not isinstance(analysis, dict):
                logger.warning("⚠️ analysis no es un diccionario válido")
                analysis = {}
            
            # Construir resultado con validación
            result = {
                "cv_info": {
                    "contacto": cv_data.get("contacto", {}),
                    "software": cv_data.get("habilidades_tecnicas", []),
                    "idiomas": [f"{lang.get('idioma', '')} ({lang.get('nivel', '')})" for lang in cv_data.get("idiomas", []) if isinstance(lang, dict)],
                    "perfil": cv_data.get("resumen_profesional", ""),
                    "experiencia": cv_data.get("experiencia", []),
                    "educacion": cv_data.get("educacion", []),
                    "habilidades": [],  # Soft skills se manejan por separado
                    "proyectos": cv_data.get("proyectos", [])
                },
                "analysis": analysis,
                "raw_text": raw_text[:1000] if raw_text else "",  # Primeros 1000 caracteres
                "full_cv_data": cv_data,
                "document_intelligence_used": True
            }
            
            logger.info("✅ Resultado compatible construido exitosamente")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error construyendo resultado compatible: {e}")
            # Devolver resultado básico en caso de error
            return {
                "cv_info": {
                    "contacto": {},
                    "software": [],
                    "idiomas": [],
                    "perfil": "",
                    "experiencia": [],
                    "educacion": [],
                    "habilidades": [],
                    "proyectos": []
                },
                "analysis": {"error": f"Error en procesamiento: {str(e)}"},
                "raw_text": raw_text[:1000] if raw_text else "",
                "full_cv_data": {},
                "document_intelligence_used": True
            }

# Función de conveniencia
def analyze_cv_with_improved_intelligence(pdf_buffer: bytes) -> Dict[str, Any]:
    """Función de conveniencia para análisis mejorado"""
    service = ImprovedDocumentIntelligenceService()
    return service.analyze_cv_with_improved_intelligence(pdf_buffer)
