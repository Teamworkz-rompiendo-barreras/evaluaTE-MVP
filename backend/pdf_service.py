# backend/pdf_service.py

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from io import BytesIO
import json
from datetime import datetime
from typing import Dict, List, Any, Optional

class PDFService:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Configurar estilos personalizados para el PDF"""
        # Estilo para títulos principales
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.darkblue
        ))
        
        # Estilo para subtítulos
        self.styles.add(ParagraphStyle(
            name='CustomSubtitle',
            parent=self.styles['Heading2'],
            fontSize=18,
            spaceAfter=20,
            textColor=colors.darkblue
        ))
        
        # Estilo para texto normal
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['Normal'],
            fontSize=12,
            spaceAfter=12,
            alignment=TA_JUSTIFY
        ))
        
        # Estilo para listas
        self.styles.add(ParagraphStyle(
            name='CustomList',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=8,
            leftIndent=20
        ))

    def create_employability_report_pdf(self, data: Dict[str, Any]) -> bytes:
        """
        Genera un PDF del informe de empleabilidad
        
        Args:
            data: Diccionario con los datos del informe
                - gameData: Lista de habilidades evaluadas
                - cvAnalysis: Análisis del CV
                - jobPreferences: Preferencias laborales
                - userInfo: Información del usuario
                - informeProfesional: Informe profesional generado por IA
        
        Returns:
            bytes: Contenido del PDF como bytes
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        
        # Lista de elementos del PDF
        story = []
        
        # Extraer datos
        game_data = data.get('gameData', [])
        cv_analysis = data.get('cvAnalysis', {})
        job_preferences = data.get('jobPreferences', {})
        user_info = data.get('userInfo', {})
        informe_profesional = data.get('informeProfesional', '')
        
        # 1. Portada
        story.extend(self._create_cover_page(user_info))
        story.append(PageBreak())
        
        # 2. Informe Profesional de IA (NUEVA SECCIÓN)
        if informe_profesional:
            story.extend(self._create_ai_professional_report(informe_profesional))
            story.append(PageBreak())
        
        # 3. Resumen ejecutivo
        story.extend(self._create_executive_summary(game_data, cv_analysis))
        story.append(PageBreak())
        
        # 4. Mapa de habilidades
        story.extend(self._create_skills_map(game_data))
        story.append(PageBreak())
        
        # 5. Análisis del CV
        story.extend(self._create_cv_analysis(cv_analysis))
        story.append(PageBreak())
        
        # 6. Preferencias laborales
        story.extend(self._create_job_preferences(job_preferences))
        story.append(PageBreak())
        
        # 7. Recomendaciones
        story.extend(self._create_recommendations(game_data, cv_analysis, job_preferences))
        
        # Generar el PDF
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
    
    def _create_cover_page(self, user_info: Dict[str, Any]) -> List:
        """Crear la página de portada"""
        elements = []
        
        # Título principal
        title = Paragraph(
            "Informe de Empleabilidad",
            self.styles['CustomTitle']
        )
        elements.append(title)
        elements.append(Spacer(1, 50))
        
        # Información del usuario
        full_name = user_info.get('fullName', 'Usuario')
        elements.append(Paragraph(
            f"<b>Nombre:</b> {full_name}",
            self.styles['CustomBody']
        ))
        elements.append(Spacer(1, 20))
        
        # Fecha
        current_date = datetime.now().strftime("%d/%m/%Y")
        elements.append(Paragraph(
            f"<b>Fecha de generación:</b> {current_date}",
            self.styles['CustomBody']
        ))
        elements.append(Spacer(1, 50))
        
        # Logo o información de la empresa
        elements.append(Paragraph(
            "EvalúaTE - Plataforma de Evaluación de Empleabilidad",
            self.styles['CustomSubtitle']
        ))
        
        return elements
    
    def _create_ai_professional_report(self, informe_profesional: str) -> List:
        """Crear la sección del informe profesional de IA"""
        elements = []
        
        # Título principal
        elements.append(Paragraph(
            "Informe Profesional de Empleabilidad",
            self.styles['CustomTitle']
        ))
        elements.append(Spacer(1, 20))
        
        # Subtítulo
        elements.append(Paragraph(
            "Análisis Integral por Psicólogo Laboral Experto en Neuroinclusión",
            self.styles['CustomSubtitle']
        ))
        elements.append(Spacer(1, 30))
        
        # Procesar el informe de IA y dividirlo en secciones
        sections = self._parse_ai_report(informe_profesional)
        
        for section_title, section_content in sections:
            # Título de sección
            elements.append(Paragraph(
                f"<b>{section_title}</b>",
                self.styles['CustomSubtitle']
            ))
            elements.append(Spacer(1, 15))
            
            # Contenido de la sección
            if isinstance(section_content, list):
                # Si es una lista, crear elementos de lista
                for item in section_content:
                    elements.append(Paragraph(
                        f"• {item}",
                        self.styles['CustomList']
                    ))
            else:
                # Si es texto, dividir en párrafos
                paragraphs = section_content.split('\n\n')
                for paragraph in paragraphs:
                    if paragraph.strip():
                        elements.append(Paragraph(
                            paragraph.strip(),
                            self.styles['CustomBody']
                        ))
                        elements.append(Spacer(1, 10))
            
            elements.append(Spacer(1, 20))
        
        return elements
    
    def _parse_ai_report(self, informe_profesional: str) -> List[tuple]:
        """Parsear el informe de IA y dividirlo en secciones"""
        sections = []
        
        # Dividir por secciones principales
        lines = informe_profesional.split('\n')
        current_section = ""
        current_content = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Detectar títulos de sección (líneas que empiezan con ## o números)
            if line.startswith('##') or (line and line[0].isdigit() and '.' in line[:5]):
                # Guardar sección anterior si existe
                if current_section and current_content:
                    sections.append((current_section, '\n'.join(current_content)))
                
                # Nueva sección
                current_section = line.replace('#', '').strip()
                current_content = []
            else:
                # Contenido de la sección actual
                current_content.append(line)
        
        # Agregar la última sección
        if current_section and current_content:
            sections.append((current_section, '\n'.join(current_content)))
        
        # Si no se encontraron secciones, tratar todo como una sección
        if not sections:
            sections.append(("Análisis Profesional", informe_profesional))
        
        return sections

    def _create_executive_summary(self, game_data: List, cv_analysis: Dict) -> List:
        """Crear el resumen ejecutivo"""
        elements = []
        
        # Título
        elements.append(Paragraph(
            "Resumen Ejecutivo",
            self.styles['CustomSubtitle']
        ))
        elements.append(Spacer(1, 20))
        
        # Calcular puntaje promedio
        if game_data:
            total_score = sum(item.get('score', 0) for item in game_data)
            avg_score = total_score / len(game_data)
            employability_level = self._get_employability_level(avg_score)
        else:
            avg_score = 0
            employability_level = "No evaluado"
        
        # Resumen de puntajes
        summary_text = f"""
        <b>Puntaje promedio de habilidades:</b> {avg_score:.1f}%
        <br/><b>Nivel de empleabilidad:</b> {employability_level}
        <br/><b>Habilidades evaluadas:</b> {len(game_data)}
        """
        
        elements.append(Paragraph(summary_text, self.styles['CustomBody']))
        elements.append(Spacer(1, 20))
        
        # Fortalezas principales
        if game_data:
            top_skills = sorted(game_data, key=lambda x: x.get('score', 0), reverse=True)[:3]
            elements.append(Paragraph("<b>Fortalezas principales:</b>", self.styles['CustomBody']))
            for skill in top_skills:
                skill_name = skill.get('skill', 'Habilidad')
                skill_score = skill.get('score', 0)
                elements.append(Paragraph(
                    f"• {skill_name}: {skill_score}%",
                    self.styles['CustomList']
                ))
        
        return elements
    
    def _create_skills_map(self, game_data: List) -> List:
        """Crear el mapa de habilidades"""
        elements = []
        
        # Título
        elements.append(Paragraph(
            "Mapa de Habilidades Evaluadas",
            self.styles['CustomSubtitle']
        ))
        elements.append(Spacer(1, 20))
        
        if not game_data:
            elements.append(Paragraph(
                "No hay datos de habilidades disponibles.",
                self.styles['CustomBody']
            ))
            return elements
        
        # Crear tabla de habilidades
        table_data = [['Habilidad', 'Puntaje', 'Nivel', 'Confianza']]
        
        for skill in game_data:
            skill_name = skill.get('skill', 'Sin nombre')
            score = skill.get('score', 0)
            level = skill.get('level', 'No evaluado')
            confidence = skill.get('confidence', 0)
            
            table_data.append([
                skill_name,
                f"{score}%",
                level.capitalize(),
                f"{confidence}%"
            ])
        
        # Crear tabla
        table = Table(table_data, colWidths=[2*inch, 1*inch, 1*inch, 1*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
        ]))
        
        elements.append(table)
        
        return elements
    
    def _create_cv_analysis(self, cv_analysis: Dict) -> List:
        """Crear la sección de análisis del CV"""
        elements = []
        
        # Título
        elements.append(Paragraph(
            "Análisis del Currículum Vitae",
            self.styles['CustomSubtitle']
        ))
        elements.append(Spacer(1, 20))
        
        if not cv_analysis:
            elements.append(Paragraph(
                "No se realizó análisis del CV.",
                self.styles['CustomBody']
            ))
            return elements
        
        # Estructura del CV
        structure = cv_analysis.get('structure', 'No evaluado')
        elements.append(Paragraph(
            f"<b>Estructura del CV:</b> {structure}",
            self.styles['CustomBody']
        ))
        
        # Coherencia
        coherence = cv_analysis.get('coherence', 'No evaluado')
        elements.append(Paragraph(
            f"<b>Coherencia:</b> {coherence}",
            self.styles['CustomBody']
        ))
        
        # Experiencia
        experience = cv_analysis.get('experience', 'No evaluado')
        elements.append(Paragraph(
            f"<b>Experiencia laboral:</b> {experience}",
            self.styles['CustomBody']
        ))
        
        elements.append(Spacer(1, 20))
        
        # Fortalezas del CV
        strengths = cv_analysis.get('strengths', [])
        if strengths:
            elements.append(Paragraph("<b>Fortalezas del CV:</b>", self.styles['CustomBody']))
            for strength in strengths:
                elements.append(Paragraph(
                    f"• {strength}",
                    self.styles['CustomList']
                ))
        
        elements.append(Spacer(1, 20))
        
        # Áreas de mejora
        weaknesses = cv_analysis.get('weaknesses', [])
        if weaknesses:
            elements.append(Paragraph("<b>Áreas de mejora:</b>", self.styles['CustomBody']))
            for weakness in weaknesses:
                elements.append(Paragraph(
                    f"• {weakness}",
                    self.styles['CustomList']
                ))
        
        # Feedback general
        feedback = cv_analysis.get('feedback', '')
        if feedback:
            elements.append(Spacer(1, 20))
            elements.append(Paragraph(
                f"<b>Feedback general:</b> {feedback}",
                self.styles['CustomBody']
            ))
        
        return elements
    
    def _create_job_preferences(self, job_preferences: Dict) -> List:
        """Crear la sección de preferencias laborales"""
        elements = []
        
        # Título
        elements.append(Paragraph(
            "Preferencias Laborales",
            self.styles['CustomSubtitle']
        ))
        elements.append(Spacer(1, 20))
        
        if not job_preferences:
            elements.append(Paragraph(
                "No se especificaron preferencias laborales.",
                self.styles['CustomBody']
            ))
            return elements
        
        # Áreas de interés
        areas = job_preferences.get('areas', [])
        if areas:
            elements.append(Paragraph("<b>Áreas de interés:</b>", self.styles['CustomBody']))
            for area in areas:
                elements.append(Paragraph(
                    f"• {area}",
                    self.styles['CustomList']
                ))
        
        elements.append(Spacer(1, 20))
        
        # Necesidades
        needs = job_preferences.get('needs', [])
        if needs:
            elements.append(Paragraph("<b>Necesidades laborales:</b>", self.styles['CustomBody']))
            for need in needs:
                elements.append(Paragraph(
                    f"• {need}",
                    self.styles['CustomList']
                ))
        
        elements.append(Spacer(1, 20))
        
        # Modalidad de trabajo
        work_mode = job_preferences.get('workMode', 'No especificado')
        elements.append(Paragraph(
            f"<b>Modalidad de trabajo preferida:</b> {work_mode.capitalize()}",
            self.styles['CustomBody']
        ))
        
        # Disponibilidad
        availability = job_preferences.get('availability', 'No especificado')
        elements.append(Paragraph(
            f"<b>Disponibilidad:</b> {availability.capitalize()}",
            self.styles['CustomBody']
        ))
        
        return elements
    
    def _create_recommendations(self, game_data: List, cv_analysis: Dict, job_preferences: Dict) -> List:
        """Crear la sección de recomendaciones"""
        elements = []
        
        # Título
        elements.append(Paragraph(
            "Recomendaciones y Próximos Pasos",
            self.styles['CustomSubtitle']
        ))
        elements.append(Spacer(1, 20))
        
        # Recomendaciones basadas en habilidades
        if game_data:
            low_skills = [skill for skill in game_data if skill.get('score', 0) < 50]
            if low_skills:
                elements.append(Paragraph("<b>Habilidades a desarrollar:</b>", self.styles['CustomBody']))
                for skill in low_skills[:3]:  # Top 3
                    skill_name = skill.get('skill', 'Habilidad')
                    elements.append(Paragraph(
                        f"• {skill_name}: Considerar formación específica",
                        self.styles['CustomList']
                    ))
        
        elements.append(Spacer(1, 20))
        
        # Recomendaciones de CV
        if cv_analysis and cv_analysis.get('weaknesses'):
            elements.append(Paragraph("<b>Mejoras sugeridas para el CV:</b>", self.styles['CustomBody']))
            for weakness in cv_analysis['weaknesses'][:3]:  # Top 3
                elements.append(Paragraph(
                    f"• {weakness}",
                    self.styles['CustomList']
                ))
        
        elements.append(Spacer(1, 20))
        
        # Próximos pasos
        elements.append(Paragraph("<b>Próximos pasos recomendados:</b>", self.styles['CustomBody']))
        next_steps = [
            "Revisar y actualizar el CV según las recomendaciones",
            "Buscar oportunidades en las áreas de interés identificadas",
            "Considerar formación adicional en habilidades con puntaje bajo",
            "Prepararse para entrevistas laborales",
            "Mantener actualizado el perfil en portales de empleo"
        ]
        
        for step in next_steps:
            elements.append(Paragraph(
                f"• {step}",
                self.styles['CustomList']
            ))
        
        return elements
    
    def _get_employability_level(self, score: float) -> str:
        """Determinar el nivel de empleabilidad basado en el puntaje"""
        if score >= 80:
            return "Excelente"
        elif score >= 60:
            return "Bueno"
        elif score >= 40:
            return "Regular"
        else:
            return "Necesita mejora"

# Función de conveniencia para usar el servicio
def create_employability_pdf(data: Dict[str, Any]) -> bytes:
    """
    Función de conveniencia para generar el PDF del informe de empleabilidad
    
    Args:
        data: Datos del informe
        
    Returns:
        bytes: Contenido del PDF
    """
    service = PDFService()
    return service.create_employability_report_pdf(data) 