#!/usr/bin/env python3
"""
Script para crear un CV de prueba en PDF para EvaluaTE MVP
"""

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.units import inch
import os

def crear_cv_prueba():
    """Crea un CV de prueba en PDF"""
    
    # Crear el documento PDF
    doc = SimpleDocTemplate("cv_prueba.pdf", pagesize=A4)
    story = []
    
    # Estilos
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=30,
        alignment=1  # Centrado
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=12,
        spaceBefore=20
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=6
    )
    
    # Título principal
    story.append(Paragraph("CURRICULUM VITAE", title_style))
    story.append(Spacer(1, 20))
    
    # Datos personales
    story.append(Paragraph("DATOS PERSONALES", heading_style))
    story.append(Paragraph("Nombre: Ana García López", normal_style))
    story.append(Paragraph("Email: ana.garcia@test.com", normal_style))
    story.append(Paragraph("Teléfono: +34 612 345 678", normal_style))
    story.append(Paragraph("LinkedIn: linkedin.com/in/anagarcia", normal_style))
    story.append(Spacer(1, 10))
    
    # Perfil profesional
    story.append(Paragraph("PERFIL PROFESIONAL", heading_style))
    story.append(Paragraph("Desarrolladora Frontend con 5 años de experiencia en creación de aplicaciones web modernas. Especializada en React, TypeScript y metodologías ágiles. Apasionada por la accesibilidad web y la experiencia de usuario.", normal_style))
    story.append(Spacer(1, 10))
    
    # Experiencia laboral
    story.append(Paragraph("EXPERIENCIA LABORAL", heading_style))
    
    story.append(Paragraph("Desarrolladora Frontend Senior", normal_style))
    story.append(Paragraph("TechCorp S.L., Madrid | 2020 - 2023", normal_style))
    story.append(Paragraph("• Lideré el desarrollo de 3 aplicaciones web con React y TypeScript", normal_style))
    story.append(Paragraph("• Optimicé el rendimiento web en un 40% implementando lazy loading", normal_style))
    story.append(Paragraph("• Mentoré a 2 desarrolladores junior en mejores prácticas", normal_style))
    story.append(Paragraph("• Colaboré en equipo de 8 personas usando metodologías ágiles", normal_style))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("Desarrolladora Frontend", normal_style))
    story.append(Paragraph("SoftServe, Barcelona | 2018 - 2020", normal_style))
    story.append(Paragraph("• Desarrollé interfaces de usuario responsivas con HTML5, CSS3 y JavaScript", normal_style))
    story.append(Paragraph("• Implementé testing automatizado con Jest y Cypress", normal_style))
    story.append(Paragraph("• Colaboré en metodologías ágiles (Scrum, Kanban)", normal_style))
    story.append(Paragraph("• Atención al cliente técnico y resolución de problemas", normal_style))
    story.append(Spacer(1, 10))
    
    # Educación
    story.append(Paragraph("EDUCACIÓN", heading_style))
    story.append(Paragraph("Grado en Ingeniería Informática", normal_style))
    story.append(Paragraph("Universidad Politécnica de Madrid | 2014 - 2018", normal_style))
    story.append(Paragraph("• Especialización en Desarrollo Web y Aplicaciones", normal_style))
    story.append(Paragraph("• Proyecto final: Plataforma de e-learning con React", normal_style))
    story.append(Paragraph("• Nota media: 8.2/10", normal_style))
    story.append(Spacer(1, 10))
    
    # Habilidades técnicas
    story.append(Paragraph("HABILIDADES TÉCNICAS", heading_style))
    story.append(Paragraph("• Frontend: React, TypeScript, JavaScript, HTML5, CSS3, Bootstrap", normal_style))
    story.append(Paragraph("• Herramientas: Git, Webpack, Jest, Cypress, VS Code", normal_style))
    story.append(Paragraph("• Metodologías: Scrum, Kanban, TDD, BDD", normal_style))
    story.append(Paragraph("• Otros: REST APIs, GraphQL, Responsive Design, PWA", normal_style))
    story.append(Spacer(1, 10))
    
    # Idiomas
    story.append(Paragraph("IDIOMAS", heading_style))
    story.append(Paragraph("• Español: Nativo", normal_style))
    story.append(Paragraph("• Inglés: C1 (TOEFL 95)", normal_style))
    story.append(Paragraph("• Francés: B1", normal_style))
    story.append(Spacer(1, 10))
    
    # Certificaciones
    story.append(Paragraph("CERTIFICACIONES", heading_style))
    story.append(Paragraph("• AWS Certified Developer Associate (2023)", normal_style))
    story.append(Paragraph("• React Developer Certification (2022)", normal_style))
    story.append(Paragraph("• Scrum Master Certified (2021)", normal_style))
    story.append(Spacer(1, 10))
    
    # Proyectos destacados
    story.append(Paragraph("PROYECTOS DESTACADOS", heading_style))
    story.append(Paragraph("• E-commerce Platform: React + Node.js + MongoDB", normal_style))
    story.append(Paragraph("• Dashboard Analytics: TypeScript + D3.js + Express", normal_style))
    story.append(Paragraph("• Mobile App: React Native + Firebase", normal_style))
    
    # Generar el PDF
    doc.build(story)
    
    print("✅ CV de prueba creado: cv_prueba.pdf")
    print("📄 Archivo listo para usar en la aplicación")
    print("📁 Ubicación:", os.path.abspath("cv_prueba.pdf"))

if __name__ == "__main__":
    crear_cv_prueba() 