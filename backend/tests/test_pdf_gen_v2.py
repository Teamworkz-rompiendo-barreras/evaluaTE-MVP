import sys
import os
import json

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from backend.new_report_schema import NewReportSchema, PersonalData, CvDetails, ImprovementArea, CvAnalysis, CvAnalysisEvidence, SuggestedRole, ActionPlan, JobSearchAdvice, UsefulTools, ReadyPhrases
    from backend.pdf_service import create_employability_pdf
except ImportError:
    # Fallback if running directly from tests folder without package context
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))
    from new_report_schema import NewReportSchema, PersonalData, CvDetails, ImprovementArea, CvAnalysis, CvAnalysisEvidence, SuggestedRole, ActionPlan, JobSearchAdvice, UsefulTools, ReadyPhrases
    from pdf_service import create_employability_pdf

def test_pdf_generation():
    print("Testing PDF Generation...")
    
    # Mock Data
    mock_report = NewReportSchema(
        summary="Resumen de prueba",
        personal_data=PersonalData(
            name="Ana Prueba Tecnología",
            location="Madrid, España",
            email="ana.prueba@example.com",
            phone="+34 600 000 000",
            disability_certificate="No",
            linkedin="linkedin.com/in/ana-prueba"
        ),
        profile_summary="Profesional con experiencia en desarrollo de software y gestión de equipos. Especialista en Python y React. Busca roles de liderazgo técnico en empresas innovadoras.",
        cv_summary="CV sólido con trayectoria coherente en empresas tecnológicas de primer nivel.",
        cv_details=CvDetails(
            experience=["Tech Lead en Startup X (2020-Presente)", "Senior Dev en Corp Y (2018-2020)"],
            education=["Grado en Ingeniería Informática (2014-2018)", "Máster en IA (2019)"],
            languages=["Español (Nativo)", "Inglés (C1)"],
            tools=["Python", "React", "Docker", "AWS"]
        ),
        strengths=["Liderazgo Técnico", "Resolución de Problemas", "Comunicación Efectiva"],
        improvement_areas=[
            ImprovementArea(area="Public Speaking", reason="Poco evidenciado", suggested_action="Dar charlas internas", score=60),
            ImprovementArea(area="Kubernetes", reason="Tecnología demandada", suggested_action="Curso avanzado", score=45)
        ],
        cv_analysis=CvAnalysis(
            structure_score=5, coherence_score=5, key_info_score=4, clarity_score=5, style_score=4,
            evidence=CvAnalysisEvidence(structure="Buena", coherence="Buena", key_info="Faltan métricas", clarity="Excelente", style="Profesional"),
            corrections=["Añadir métricas de impacto"],
            reordering_suggestions=[]
        ),
        ideal_work_environment="Entorno híbrido, cultura colaborativa, foco en calidad.",
        suggested_roles=[
            SuggestedRole(role="Engineering Manager", reason="Perfil natural para el puesto", seniority="Senior", remote_viable=True),
            SuggestedRole(role="Principal Engineer", reason="Alternativa técnica", seniority="Principal", remote_viable=True)
        ],
        action_plan=ActionPlan(
            short_term=["Actualizar LinkedIn", "Preparar pitch"],
            medium_term=["Certificación AWS", "Networking"],
            long_term=["Rol de CTO", "Mentoring"]
        ),
        job_search_advice=JobSearchAdvice(
            cv_optimization=["Resaltar logros"],
            recommended_platforms=["LinkedIn", "Manfred"],
            networking="Asistir a meetups locales"
        ),
        useful_tools=UsefulTools(
            productivity=["Notion", "Linear"],
            job_search=["LinkedIn Jobs"],
            learning=["Coursera", "O'Reilly"],
            accessibility=["Screen reader friendly"]
        ),
        completed_games=["Juego de Liderazgo", "Test de Lógica"],
        ready_phrases=ReadyPhrases(
            headline="Tech Lead | Python & React Expert",
            about_me="Apasionada por la tecnología...",
            short_message="Hola, me interesa tu oferta..."
        ),
        final_message="¡Tienes un perfil excelente, sigue así!",
        employability_score=85,
        soft_skills=[
            {"skill": "Liderazgo", "score": 90},
            {"skill": "Comunicación", "score": 85},
            {"skill": "Trabajo en Equipo", "score": 88},
            {"skill": "Resolución de Problemas", "score": 92},
            {"skill": "Adaptabilidad", "score": 75},
            {"skill": "Creatividad", "score": 70}
        ]
    )

    try:
        pdf_bytes = create_employability_pdf(mock_report)
        print(f"PDF Generated Successfully. Size: {len(pdf_bytes)} bytes")
        
        # Save for manual inspection if possible
        output_path = os.path.join(os.path.dirname(__file__), "test_report_v2.pdf")
        with open(output_path, "wb") as f:
            f.write(pdf_bytes)
        print(f"PDF saved to {output_path}")
        
    except Exception as e:
        print(f"ERROR generating PDF: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_pdf_generation()
