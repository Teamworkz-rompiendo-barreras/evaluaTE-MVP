
import asyncio
import os
import sys
from io import BytesIO
from reportlab.pdfgen import canvas

# Ensure backend imports work
sys.path.append(os.getcwd())

from backend.cv_analyzer import extract_pdf_info
from backend.generate_report import _generate_structured_response_from_data
from backend.pdf_service import create_employability_pdf

def create_dummy_pdf():
    buffer = BytesIO()
    c = canvas.Canvas(buffer)
    c.drawString(100, 800, "Curriculum Vitae")
    c.drawString(100, 780, "Nombre: Microsoft Office Photoshop In")  # The problematic name
    c.drawString(100, 760, "Email: test@example.com")
    c.drawString(100, 740, "Experiencia Laboral:")
    c.drawString(100, 720, "- Empresa A: Desarrollador (2020-2021)")
    c.drawString(100, 700, "- Empresa B: Ingeniero (2021-Presente)")
    c.drawString(100, 680, "Educación:")
    c.drawString(100, 660, "- Universidad X: Grado en Informática")
    c.drawString(100, 640, "Habilidades:")
    c.drawString(100, 620, "- Python, JavaScript, SQL")
    c.save()
    buffer.seek(0)
    return buffer.read()

async def run_simulation():
    print("--- 1. Generating Dummy PDF with 'Bad' Name ---")
    pdf_bytes = create_dummy_pdf()
    print(f"PDF generated ({len(pdf_bytes)} bytes).")

    print("\n--- 2. Running extraction (extract_pdf_info) ---")
    extracted_data = await extract_pdf_info(pdf_bytes)
    
    print("Raw extracted candidate (from CV analyzer):", extracted_data.get("candidate"))
    print("Raw extracted contact name:", extracted_data.get("contact", {}).get("name"))

    print("\n--- 3. Applying Main.py Sanitization Logic ---")
    # Replicating logic from backend/main.py
    normalized = extracted_data
    suspicious_keywords = {
        "microsoft", "office", "adobe", "photoshop", "suite", "tool", "software", "windows", "linux", "macos",
        "visual", "studio", "code", "python", "java", "javascript", "html", "css", "sql", "react", "node",
        "word", "excel", "powerpoint", "paint", "movie maker", "curriculum", "vitae", "resume"
    }

    candidates_names = []
    if isinstance(normalized.get("contact"), dict):
        candidates_names.append(normalized["contact"].get("name"))
    if normalized.get("candidate"):
        candidates_names.append(normalized.get("candidate"))

    valid_name = "Candidato"
    for name in candidates_names:
        if not name: continue
        name_lower = str(name).lower()
        if any(k in name_lower for k in suspicious_keywords):
            print(f"  -> Rejected name '{name}' due to keyword match.")
            continue
        if len(name) > 50 or any(ch.isdigit() for ch in name):
            print(f"  -> Rejected name '{name}' due to length/digits.")
            continue
        valid_name = name
        break
    
    print(f"  -> Final Valid Name: '{valid_name}'")

    if isinstance(normalized.get("contact"), dict):
        normalized["contact"]["name"] = valid_name
    normalized["candidate"] = valid_name

    print("\n--- 4. Generating Report Data ---")
    # Mock parameters for report generation
    candidate_data = {"fullName": valid_name}
    report_schema = _generate_structured_response_from_data(
        candidate_data=candidate_data,
        soft_skills_data=[], # mock
        cv_data=normalized,
        job_preferences_data={},
        employability_score=75,
        level="Alto",
        completed_games=[]
    )
    
    print("Report generated for:", report_schema.personal_data.name)
    print("CV Details present:", bool(report_schema.cv_details))
    if report_schema.cv_details:
        print("Experience entries:", len(report_schema.cv_details.get("experience", [])))

    print("\n--- 5. Generating PDF ---")
    try:
        pdf_bytes = create_employability_pdf(report_schema)
        print(f"PDF successfully generated ({len(pdf_bytes)} bytes).")
    except Exception as e:
        print("PDF Generation Failed:", e)

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    asyncio.run(run_simulation())
