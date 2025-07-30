#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
document_intelligence.py

Módulo para el análisis de CVs usando Azure AI Document Intelligence (Form Recognizer).
Este módulo proporciona una extracción más precisa y estructurada de información
de CVs comparado con OCR tradicional.
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional
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
    logger.warning("Azure AI Document Intelligence no disponible. Instala azure-ai-formrecognizer")

class DocumentIntelligenceService:
    """
    Servicio para análisis de documentos usando Azure AI Document Intelligence
    """
    
    def __init__(self):
        self.endpoint = os.getenv('AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT')
        self.key = os.getenv('AZURE_DOCUMENT_INTELLIGENCE_KEY')
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
        
        if self.storage_connection_string:
            try:
                self.blob_service_client = BlobServiceClient.from_connection_string(
                    self.storage_connection_string
                )
                logger.info("✅ Azure Storage configurado correctamente")
            except Exception as e:
                logger.error(f"❌ Error configurando Azure Storage: {e}")
                self.blob_service_client = None
    
    def is_configured(self) -> bool:
        """Verifica si el servicio está configurado correctamente"""
        return self.client is not None
    
    def analyze_cv_with_document_intelligence(self, pdf_buffer: bytes) -> Dict[str, Any]:
        """
        Analiza un CV usando Azure AI Document Intelligence
        
        Args:
            pdf_buffer: Contenido del PDF como bytes
            
        Returns:
            Dict con la información extraída del CV
        """
        if not self.is_configured():
            return {
                "error": "Azure AI Document Intelligence no está configurado",
                "cv_info": {},
                "analysis": {},
                "raw_text": ""
            }
        
        try:
            logger.info("🚀 Iniciando análisis con Azure AI Document Intelligence...")
            
            # Crear archivo temporal para el análisis
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
                temp_file.write(pdf_buffer)
                temp_file_path = temp_file.name
            
            try:
                # Analizar documento con Document Intelligence
                with open(temp_file_path, "rb") as document:
                    poller = self.client.begin_analyze_document(
                        "prebuilt-document", document
                    )
                    result = poller.result()
                
                # Extraer información estructurada
                cv_data = self._extract_structured_data(result)
                
                # Analizar estructura y calidad
                analysis = self._analyze_cv_structure(cv_data)
                
                # Construir resultado compatible
                cv_info = self._build_compatible_result(cv_data)
                
                logger.info("✅ Análisis con Document Intelligence completado")
                logger.info(f"📊 Resumen: {len(cv_info.get('software', []))} habilidades técnicas, "
                          f"{len(cv_info.get('experiencia', []))} experiencias, "
                          f"{len(cv_data.get('education', []))} formación")
                
                return {
                    "cv_info": cv_info,
                    "analysis": analysis,
                    "raw_text": cv_data.get("raw_text", ""),
                    "full_cv_data": cv_data,
                    "document_intelligence_used": True
                }
                
            finally:
                # Limpiar archivo temporal
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
                    
        except Exception as e:
            logger.error(f"❌ Error en análisis con Document Intelligence: {str(e)}")
            return {
                "error": f"Error en análisis con Document Intelligence: {str(e)}",
                "cv_info": {},
                "analysis": {},
                "raw_text": "",
                "document_intelligence_used": False
            }
    
    def _extract_structured_data(self, result) -> Dict[str, Any]:
        """
        Extrae datos estructurados del resultado de Document Intelligence
        """
        cv_data = {
            "contact": {},
            "education": [],
            "experience": [],
            "skills": [],
            "languages": [],
            "projects": [],
            "raw_text": "",
            "sections": {}
        }
        
        # Extraer texto completo
        if result.content:
            cv_data["raw_text"] = result.content
        
        # Extraer información de contacto
        cv_data["contact"] = self._extract_contact_info(result)
        
        # Extraer secciones del CV
        cv_data["sections"] = self._extract_sections(result)
        
        # Extraer educación
        cv_data["education"] = self._extract_education(result)
        
        # Extraer experiencia laboral
        cv_data["experience"] = self._extract_experience(result)
        
        # Extraer habilidades
        cv_data["skills"] = self._extract_skills(result)
        
        # Extraer idiomas
        cv_data["languages"] = self._extract_languages(result)
        
        # Extraer proyectos
        cv_data["projects"] = self._extract_projects(result)
        
        return cv_data
    
    def _extract_contact_info(self, result) -> Dict[str, str]:
        """Extrae información de contacto"""
        contact = {}
        
        # Buscar patrones de email
        for line in result.content.split('\n'):
            if '@' in line and '.' in line:
                # Patrón básico de email
                import re
                email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', line)
                if email_match:
                    contact["email"] = email_match.group()
            
            # Buscar teléfonos
            if any(char.isdigit() for char in line) and len(line.strip()) > 8:
                import re
                phone_match = re.search(r'[\+]?[0-9\s\-\(\)]{8,}', line)
                if phone_match:
                    contact["phone"] = phone_match.group().strip()
        
        return contact
    
    def _extract_sections(self, result) -> Dict[str, str]:
        """Extrae secciones del CV basándose en encabezados"""
        sections = {}
        current_section = "general"
        current_content = []
        
        for line in result.content.split('\n'):
            line = line.strip()
            if not line:
                continue
            
            # Detectar encabezados de sección
            section_keywords = {
                "educación": ["educación", "formación", "académica", "estudios"],
                "experiencia": ["experiencia", "laboral", "trabajo", "empleo"],
                "habilidades": ["habilidades", "skills", "competencias", "tecnologías"],
                "idiomas": ["idiomas", "languages", "idioma"],
                "proyectos": ["proyectos", "portfolio", "trabajos"],
                "contacto": ["contacto", "información personal", "datos personales"]
            }
            
            is_header = False
            for section_name, keywords in section_keywords.items():
                if any(keyword in line.lower() for keyword in keywords):
                    if current_content:
                        sections[current_section] = '\n'.join(current_content)
                    current_section = section_name
                    current_content = []
                    is_header = True
                    break
            
            if not is_header:
                current_content.append(line)
        
        # Guardar la última sección
        if current_content:
            sections[current_section] = '\n'.join(current_content)
        
        return sections
    
    def _extract_education(self, result) -> List[Dict[str, str]]:
        """Extrae información de educación"""
        education = []
        
        # Buscar en la sección de educación
        education_section = ""
        for line in result.content.split('\n'):
            if any(keyword in line.lower() for keyword in ["educación", "formación", "académica", "estudios"]):
                # Encontrar el contenido de la sección
                lines = result.content.split('\n')
                start_idx = lines.index(line)
                for i in range(start_idx + 1, len(lines)):
                    if any(keyword in lines[i].lower() for keyword in ["experiencia", "habilidades", "proyectos"]):
                        break
                    education_section += lines[i] + '\n'
                break
        
        # Parsear información de educación
        if education_section:
            lines = education_section.split('\n')
            current_edu = {}
            
            for line in lines:
                line = line.strip()
                if not line:
                    if current_edu:
                        education.append(current_edu)
                        current_edu = {}
                    continue
                
                # Detectar título, institución, año
                if any(keyword in line.lower() for keyword in ["grado", "licenciatura", "máster", "doctorado", "ingeniería"]):
                    current_edu["title"] = line
                elif any(keyword in line.lower() for keyword in ["universidad", "instituto", "escuela"]):
                    current_edu["institution"] = line
                elif any(char.isdigit() for char in line) and len(line) <= 4:
                    current_edu["year"] = line
            
            if current_edu:
                education.append(current_edu)
        
        return education
    
    def _extract_experience(self, result) -> List[Dict[str, str]]:
        """Extrae información de experiencia laboral"""
        experience = []
        
        # Buscar en la sección de experiencia
        experience_section = ""
        for line in result.content.split('\n'):
            if any(keyword in line.lower() for keyword in ["experiencia", "laboral", "trabajo", "empleo"]):
                # Encontrar el contenido de la sección
                lines = result.content.split('\n')
                start_idx = lines.index(line)
                for i in range(start_idx + 1, len(lines)):
                    if any(keyword in lines[i].lower() for keyword in ["educación", "habilidades", "proyectos"]):
                        break
                    experience_section += lines[i] + '\n'
                break
        
        # Parsear información de experiencia
        if experience_section:
            lines = experience_section.split('\n')
            current_exp = {}
            
            for line in lines:
                line = line.strip()
                if not line:
                    if current_exp:
                        experience.append(current_exp)
                        current_exp = {}
                    continue
                
                # Detectar empresa, puesto, período
                if any(keyword in line.lower() for keyword in ["s.a.", "s.l.", "ltd", "inc", "corp"]):
                    current_exp["company"] = line
                elif any(keyword in line.lower() for keyword in ["desarrollador", "analista", "ingeniero", "consultor"]):
                    current_exp["position"] = line
                elif any(char.isdigit() for char in line) and any(keyword in line.lower() for keyword in ["202", "201", "200"]):
                    current_exp["period"] = line
            
            if current_exp:
                experience.append(current_exp)
        
        return experience
    
    def _extract_skills(self, result) -> List[str]:
        """Extrae habilidades técnicas"""
        skills = []
        
        # Buscar en la sección de habilidades
        skills_section = ""
        for line in result.content.split('\n'):
            if any(keyword in line.lower() for keyword in ["habilidades", "skills", "competencias", "tecnologías"]):
                # Encontrar el contenido de la sección
                lines = result.content.split('\n')
                start_idx = lines.index(line)
                for i in range(start_idx + 1, len(lines)):
                    if any(keyword in lines[i].lower() for keyword in ["experiencia", "educación", "proyectos"]):
                        break
                    skills_section += lines[i] + '\n'
                break
        
        # Parsear habilidades
        if skills_section:
            # Buscar tecnologías comunes
            tech_keywords = [
                "javascript", "python", "java", "c++", "c#", "php", "ruby", "go", "rust",
                "react", "angular", "vue", "node.js", "express", "django", "flask",
                "sql", "mysql", "postgresql", "mongodb", "redis",
                "html", "css", "bootstrap", "tailwind", "sass", "less",
                "git", "docker", "kubernetes", "aws", "azure", "gcp",
                "machine learning", "ai", "data science", "analytics"
            ]
            
            for line in skills_section.split('\n'):
                line_lower = line.lower()
                for tech in tech_keywords:
                    if tech in line_lower:
                        skills.append(tech.title())
        
        return list(set(skills))  # Eliminar duplicados
    
    def _extract_languages(self, result) -> List[Dict[str, str]]:
        """Extrae información de idiomas"""
        languages = []
        
        # Buscar en la sección de idiomas
        languages_section = ""
        for line in result.content.split('\n'):
            if any(keyword in line.lower() for keyword in ["idiomas", "languages", "idioma"]):
                # Encontrar el contenido de la sección
                lines = result.content.split('\n')
                start_idx = lines.index(line)
                for i in range(start_idx + 1, len(lines)):
                    if any(keyword in lines[i].lower() for keyword in ["experiencia", "habilidades", "proyectos"]):
                        break
                    languages_section += lines[i] + '\n'
                break
        
        # Parsear idiomas
        if languages_section:
            language_names = ["español", "inglés", "francés", "alemán", "italiano", "portugués"]
            levels = ["nativo", "fluente", "avanzado", "intermedio", "básico", "a1", "a2", "b1", "b2", "c1", "c2"]
            
            for line in languages_section.split('\n'):
                line_lower = line.lower()
                for lang in language_names:
                    if lang in line_lower:
                        level = "intermedio"  # Por defecto
                        for lvl in levels:
                            if lvl in line_lower:
                                level = lvl
                                break
                        languages.append({"language": lang, "level": level})
                        break
        
        return languages
    
    def _extract_projects(self, result) -> List[Dict[str, str]]:
        """Extrae información de proyectos"""
        projects = []
        
        # Buscar en la sección de proyectos
        projects_section = ""
        for line in result.content.split('\n'):
            if any(keyword in line.lower() for keyword in ["proyectos", "portfolio", "trabajos"]):
                # Encontrar el contenido de la sección
                lines = result.content.split('\n')
                start_idx = lines.index(line)
                for i in range(start_idx + 1, len(lines)):
                    if any(keyword in lines[i].lower() for keyword in ["experiencia", "habilidades", "educación"]):
                        break
                    projects_section += lines[i] + '\n'
                break
        
        # Parsear proyectos
        if projects_section:
            lines = projects_section.split('\n')
            current_project = {}
            
            for line in lines:
                line = line.strip()
                if not line:
                    if current_project:
                        projects.append(current_project)
                        current_project = {}
                    continue
                
                # Detectar nombre de proyecto, descripción, tecnologías
                if len(line) > 10 and not any(char.isdigit() for char in line[:5]):
                    current_project["name"] = line
                elif any(keyword in line.lower() for keyword in ["desarrollado", "creado", "implementado"]):
                    current_project["description"] = line
            
            if current_project:
                projects.append(current_project)
        
        return projects
    
    def _analyze_cv_structure(self, cv_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analiza la estructura y calidad del CV"""
        analysis = {
            "structure_score": 0,
            "completeness_score": 0,
            "quality_score": 0,
            "strengths": [],
            "weaknesses": [],
            "recommendations": []
        }
        
        # Calcular puntuaciones
        scores = {
            "contact": 20 if cv_data.get("contact") else 0,
            "education": 20 if cv_data.get("education") else 0,
            "experience": 25 if cv_data.get("experience") else 0,
            "skills": 20 if cv_data.get("skills") else 0,
            "languages": 10 if cv_data.get("languages") else 0,
            "projects": 5 if cv_data.get("projects") else 0
        }
        
        analysis["structure_score"] = sum(scores.values())
        analysis["completeness_score"] = len([s for s in scores.values() if s > 0]) * 16.67
        
        # Identificar fortalezas y debilidades
        if scores["contact"] > 0:
            analysis["strengths"].append("Información de contacto presente")
        else:
            analysis["weaknesses"].append("Falta información de contacto")
        
        if scores["education"] > 0:
            analysis["strengths"].append("Formación académica documentada")
        else:
            analysis["weaknesses"].append("Falta información de formación académica")
        
        if scores["experience"] > 0:
            analysis["strengths"].append("Experiencia laboral documentada")
        else:
            analysis["weaknesses"].append("Falta información de experiencia laboral")
        
        if scores["skills"] > 0:
            analysis["strengths"].append("Habilidades técnicas identificadas")
        else:
            analysis["weaknesses"].append("Falta información de habilidades técnicas")
        
        # Calcular puntuación de calidad
        analysis["quality_score"] = (analysis["structure_score"] + analysis["completeness_score"]) / 2
        
        # Generar recomendaciones
        if analysis["quality_score"] < 50:
            analysis["recommendations"].append("El CV necesita más información y estructura")
        elif analysis["quality_score"] < 75:
            analysis["recommendations"].append("El CV es aceptable pero puede mejorarse")
        else:
            analysis["recommendations"].append("El CV tiene una buena estructura y contenido")
        
        return analysis
    
    def _build_compatible_result(self, cv_data: Dict[str, Any]) -> Dict[str, Any]:
        """Construye un resultado compatible con el formato esperado"""
        return {
            "contacto": cv_data.get("contact", {}),
            "software": cv_data.get("skills", []),
            "idiomas": [f"{lang.get('language', '')} ({lang.get('level', '')})" 
                       for lang in cv_data.get("languages", [])],
            "perfil": cv_data.get("raw_text", "")[:200] + "..." if len(cv_data.get("raw_text", "")) > 200 else cv_data.get("raw_text", ""),
            "experiencia": cv_data.get("experience", []),
            "educacion": cv_data.get("education", []),
            "habilidades": [],  # Habilidades blandas se extraen de otra manera
            "proyectos": cv_data.get("projects", [])
        }

# Instancia global del servicio
document_intelligence_service = DocumentIntelligenceService()

def analyze_cv_with_document_intelligence(pdf_buffer: bytes) -> Dict[str, Any]:
    """
    Función de conveniencia para analizar CVs con Document Intelligence
    """
    return document_intelligence_service.analyze_cv_with_document_intelligence(pdf_buffer) 