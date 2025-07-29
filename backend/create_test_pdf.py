#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para crear un PDF de prueba con texto real para verificar el análisis de CV.
"""

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
import os

def create_test_cv_pdf():
    """Crea un PDF de prueba con contenido de CV real"""
    
    filename = "test_cv_real.pdf"
    
    # Crear el PDF
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter
    
    # Configurar fuente
    c.setFont("Helvetica", 12)
    
    # Título
    c.setFont("Helvetica-Bold", 18)
    c.drawString(1*inch, 10*inch, "CURRICULUM VITAE")
    
    # Información personal
    c.setFont("Helvetica-Bold", 14)
    c.drawString(1*inch, 9.5*inch, "DATOS PERSONALES")
    
    c.setFont("Helvetica", 12)
    c.drawString(1*inch, 9.2*inch, "Nombre: María García López")
    c.drawString(1*inch, 9*inch, "Email: maria.garcia@email.com")
    c.drawString(1*inch, 8.8*inch, "Teléfono: +34 612 345 678")
    c.drawString(1*inch, 8.6*inch, "Ubicación: Madrid, España")
    
    # Perfil profesional
    c.setFont("Helvetica-Bold", 14)
    c.drawString(1*inch, 8.2*inch, "PERFIL PROFESIONAL")
    
    c.setFont("Helvetica", 12)
    profile_text = "Desarrolladora frontend con 3 años de experiencia en React, JavaScript y TypeScript. Especializada en crear interfaces de usuario responsivas y accesibles. Experiencia en trabajo en equipo y metodologías ágiles."
    
    # Dividir texto en líneas
    words = profile_text.split()
    lines = []
    current_line = ""
    
    for word in words:
        test_line = current_line + " " + word if current_line else word
        if len(test_line) < 60:  # Aproximadamente 60 caracteres por línea
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word
    
    if current_line:
        lines.append(current_line)
    
    y_position = 7.8*inch
    for line in lines:
        c.drawString(1*inch, y_position, line)
        y_position -= 0.2*inch
    
    # Experiencia laboral
    c.setFont("Helvetica-Bold", 14)
    c.drawString(1*inch, 7.2*inch, "EXPERIENCIA LABORAL")
    
    c.setFont("Helvetica-Bold", 12)
    c.drawString(1*inch, 6.9*inch, "Desarrolladora Frontend - TechCorp")
    c.setFont("Helvetica", 10)
    c.drawString(1*inch, 6.7*inch, "Enero 2022 - Presente")
    
    c.setFont("Helvetica", 12)
    exp_text = "• Desarrollo de aplicaciones web con React y TypeScript"
    c.drawString(1.2*inch, 6.5*inch, exp_text)
    c.drawString(1.2*inch, 6.3*inch, "• Implementación de diseño responsivo y accesible")
    c.drawString(1.2*inch, 6.1*inch, "• Colaboración con equipo de diseño y backend")
    c.drawString(1.2*inch, 5.9*inch, "• Optimización de rendimiento y SEO")
    
    # Formación académica
    c.setFont("Helvetica-Bold", 14)
    c.drawString(1*inch, 5.3*inch, "FORMACIÓN ACADÉMICA")
    
    c.setFont("Helvetica-Bold", 12)
    c.drawString(1*inch, 5*inch, "Grado en Ingeniería Informática")
    c.setFont("Helvetica", 10)
    c.drawString(1*inch, 4.8*inch, "Universidad Politécnica de Madrid")
    c.drawString(1*inch, 4.6*inch, "2018 - 2022")
    
    # Habilidades técnicas
    c.setFont("Helvetica-Bold", 14)
    c.drawString(1*inch, 4*inch, "HABILIDADES TÉCNICAS")
    
    c.setFont("Helvetica", 12)
    c.drawString(1*inch, 3.7*inch, "Lenguajes: JavaScript, TypeScript, HTML5, CSS3")
    c.drawString(1*inch, 3.5*inch, "Frameworks: React, Vue.js, Angular")
    c.drawString(1*inch, 3.3*inch, "Herramientas: Git, Webpack, Jest, Cypress")
    c.drawString(1*inch, 3.1*inch, "Bases de datos: MongoDB, PostgreSQL")
    c.drawString(1*inch, 2.9*inch, "Cloud: AWS, Azure, Docker")
    
    # Habilidades blandas
    c.setFont("Helvetica-Bold", 14)
    c.drawString(1*inch, 2.3*inch, "HABILIDADES BLANDAS")
    
    c.setFont("Helvetica", 12)
    c.drawString(1*inch, 2*inch, "• Trabajo en equipo y colaboración")
    c.drawString(1*inch, 1.8*inch, "• Comunicación efectiva")
    c.drawString(1*inch, 1.6*inch, "• Resolución de problemas")
    c.drawString(1*inch, 1.4*inch, "• Aprendizaje continuo")
    c.drawString(1*inch, 1.2*inch, "• Gestión del tiempo")
    
    # Idiomas
    c.setFont("Helvetica-Bold", 14)
    c.drawString(1*inch, 0.6*inch, "IDIOMAS")
    
    c.setFont("Helvetica", 12)
    c.drawString(1*inch, 0.3*inch, "Español: Nativo")
    c.drawString(1*inch, 0.1*inch, "Inglés: Avanzado (C1)")
    
    # Guardar el PDF
    c.save()
    
    print(f"✅ PDF de prueba creado: {filename}")
    print(f"📄 Tamaño del archivo: {os.path.getsize(filename)} bytes")
    
    return filename

if __name__ == "__main__":
    create_test_cv_pdf() 