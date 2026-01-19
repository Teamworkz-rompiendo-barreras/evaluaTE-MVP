
import asyncio
import os
import sys
import json
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors

# Ensure backend imports work
sys.path.append(os.getcwd())

from backend.cv_analyzer import analyze_cv_with_ai

def create_complex_pdf():
    """Crea un PDF con diseño de dos columnas para probar la extracción multimodal."""
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    # --- Columna Izquierda (Fondo Oscuro) ---
    c.setFillColor(colors.black)
    c.rect(0, 0, width/3, height, fill=1)
    
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(20, height - 50, "CONTACTO")
    
    c.setFont("Helvetica", 10)
    c.drawString(20, height - 80, "juan.perez@ejemplo.com")
    c.drawString(20, height - 100, "+34 600 000 000")
    c.drawString(20, height - 120, "Madrid, España")
    
    c.setFont("Helvetica-Bold", 14)
    c.drawString(20, height - 180, "HABILIDADES")
    c.setFont("Helvetica", 10)
    c.drawString(20, height - 210, "• Python (Experto)")
    c.drawString(20, height - 230, "• React (Avanzado)")
    c.drawString(20, height - 250, "• Docker (Intermedio)")
    
    # --- Columna Derecha (Fondo Claro) ---
    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 24)
    c.drawString(width/3 + 20, height - 50, "JUAN PÉREZ")
    c.setFont("Helvetica", 16)
    c.drawString(width/3 + 20, height - 75, "Full Stack Developer")
    
    c.setFont("Helvetica-Bold", 14)
    c.drawString(width/3 + 20, height - 140, "EXPERIENCIA PROFESIONAL")
    
    # Experiencia 1
    c.setFont("Helvetica-Bold", 12)
    c.drawString(width/3 + 20, height - 170, "Tech Solutions S.L. - Senior Developer")
    c.setFont("Helvetica-Oblique", 10)
    c.drawString(width/3 + 20, height - 185, "Enero 2022 - Presente")
    c.setFont("Helvetica", 10)
    c.drawString(width/3 + 20, height - 205, "• Lideré la migración a microservicios reduciendo latencia un 40%.")
    c.drawString(width/3 + 20, height - 220, "• Implementé CI/CD con GitHub Actions.")

    # Experiencia 2
    c.setFont("Helvetica-Bold", 12)
    c.drawString(width/3 + 20, height - 260, "WebApps Inc. - Junior Developer")
    c.setFont("Helvetica-Oblique", 10)
    c.drawString(width/3 + 20, height - 275, "Junio 2020 - Diciembre 2021")
    c.setFont("Helvetica", 10)
    c.drawString(width/3 + 20, height - 295, "• Desarrollo de frontend con React y Redux.")
    
    c.save()
    buffer.seek(0)
    return buffer.read()

async def run_test():
    print("--- 1. Generando PDF complejo (2 columnas) ---")
    pdf_bytes = create_complex_pdf()
    print(f"PDF generado: {len(pdf_bytes)} bytes")
    
    # Guardar para inspección visual si se desea
    with open("test_complex_cv.pdf", "wb") as f:
        f.write(pdf_bytes)
    print("PDF guardado como 'test_complex_cv.pdf' para referencia.")
    
    print("\n--- 2. Enviando a Gemini (Modo Multimodal) ---")
    # Pasamos texto vacío para forzar que use el PDF, o texto mínimo
    # En la implementación real, extract_pdf_info extrae texto plano TAMBIÉN.
    # Aquí simulamos que no pudimos extraer texto perfecto, o pasamos texto sucio.
    dummy_text = "JUAN PEREZ Python React..." # Texto plano muy básico/roto
    
    try:
        result = analyze_cv_with_ai(dummy_text, pdf_bytes)
        
        print("\n--- 3. Resultados de Extracción ---")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        # Verificaciones clave
        print("\n--- Verificación ---")
        name = result.get("contacto", {}).get("nombre")
        skills = result.get("habilidades_tecnicas", [])
        exp = result.get("experiencia_laboral", [])
        
        print(f"Nombre detectado: {name} (Esperado: Juan Pérez)")
        print(f"Habilidades detectadas: {len(skills)} (Esperado: ~3)")
        print(f"Experiencias detectadas: {len(exp)} (Esperado: 2)")
        
        if name == "Juan Pérez" or "Juan" in str(name):
             print("✅ Test de Nombre PASADO")
        else:
             print("❌ Test de Nombre FALLADO")
             
    except Exception as e:
        print(f"❌ Error durante el test: {e}")

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    asyncio.run(run_test())
